import logging
import time
from collections.abc import Generator
from contextlib import closing
from urllib.parse import quote

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from config import Config
from .base_storage import BaseStorage

logger = logging.getLogger(__name__)


class S3Storage(BaseStorage):
    def __init__(self) -> None:
        super().__init__()
        self.bucket = Config.S3_BUCKET
        self.region = Config.AWS_REGION
        self.access_key = Config.AWS_ACCESS_KEY_ID
        self.secret_key = Config.AWS_SECRET_ACCESS_KEY
        self.client = boto3.client(
            's3',
            aws_secret_access_key=self.secret_key,
            aws_access_key_id=self.access_key,
            region_name=self.region,
        )
    
    def save(self, filename: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=filename, Body=data)

    def load_once(self, filename: str) -> bytes:
        try:
            with closing(self.client) as client:
                data = client.get_object(Bucket=self.bucket, Key=filename)['Body'].read()
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError("File not found")
            else:
                raise
        return data

    def load_stream(self, filename: str) -> Generator:
        def generate(filename: str = filename) -> Generator:
            try:
                with closing(self.client) as client:
                    response = client.get_object(Bucket=self.bucket, Key=filename)
                    yield from response['Body'].iter_chunks()
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    raise FileNotFoundError("File not found")
                else:
                    raise
        return generate()

    def download(self, filename: str, target_filepath: str) -> None:
        with closing(self.client) as client:
            client.download_file(self.bucket, filename, target_filepath)

    def get_path(self, object_key: str, filename: str = "") -> str:
        download_filename = "document.pdf"
        if len(filename) > 4:
            download_filename = filename
        encoded_filename = quote(download_filename)
        signed_url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': object_key,
                    'ResponseContentDisposition': f'attachment; filename="{encoded_filename}"'},
        )
        return signed_url

    def exists(self, filename: str) -> bool:
        try:
            with closing(self.client) as client:
                client.head_object(Bucket=self.bucket, Key=filename)
                return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logging.info(f"S3 object ({filename}) not found in bucket {self.bucket}")
            else:
                logging.error(f"Error checking existence of object {filename} in bucket {self.bucket}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error checking S3 object ({filename}) in bucket {self.bucket}: {e}")
            return False

    def delete(self, filename: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=filename)


class TextractWrapper:
    """Encapsulates Textract functions."""

    def __init__(self, textract_client=None, s3_resource=None, sqs_resource=None):
        """
        Initialize TextractWrapper with AWS clients.
        
        If clients are not provided, they will be created using Config credentials.
        
        :param textract_client: A Boto3 Textract client (optional).
        :param s3_resource: A Boto3 Amazon S3 resource (optional).
        :param sqs_resource: A Boto3 Amazon SQS resource (optional).
        """
        self.region = Config.AWS_REGION
        self.access_key = Config.AWS_ACCESS_KEY_ID
        self.secret_key = Config.AWS_SECRET_ACCESS_KEY
        
        # Initialize clients if not provided
        if textract_client is None:
            self.textract_client = boto3.client(
                'textract',
                aws_secret_access_key=self.secret_key,
                aws_access_key_id=self.access_key,
                region_name=self.region,
            )
        else:
            self.textract_client = textract_client
            
        if s3_resource is None:
            self.s3_resource = boto3.resource(
                's3',
                aws_secret_access_key=self.secret_key,
                aws_access_key_id=self.access_key,
                region_name=self.region,
            )
        else:
            self.s3_resource = s3_resource
            
        if sqs_resource is None:
            self.sqs_resource = boto3.resource(
                'sqs',
                aws_secret_access_key=self.secret_key,
                aws_access_key_id=self.access_key,
                region_name=self.region,
            )
        else:
            self.sqs_resource = sqs_resource

    def detect_file_text(self, *, document_file_name=None, document_bytes=None):
        """
        Detects text elements in a local image file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        if document_file_name is not None:
            with open(document_file_name, "rb") as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.detect_document_text(
                Document={"Bytes": document_bytes}
            )
            logger.info("Detected %s blocks.", len(response["Blocks"]))
        except ClientError:
            logger.exception("Couldn't detect text.")
            raise
        else:
            return response

    def start_document_text_detection_from_s3(self, bucket: str, document_key: str) -> str:
        """
        Starts an asynchronous document text detection job for a document in S3.
        
        :param bucket: The S3 bucket name.
        :param document_key: The S3 object key (path) of the document.
        :return: The job ID for tracking the detection process.
        """
        try:
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    "S3Object": {
                        "Bucket": bucket,
                        "Name": document_key
                    }
                }
            )
            job_id = response["JobId"]
            logger.info(f"Textract job started: {job_id} for s3://{bucket}/{document_key}")
            return job_id
        except ClientError:
            logger.exception(f"Couldn't start text detection job for s3://{bucket}/{document_key}")
            raise

    def wait_for_completion(self, job_id: str, poll_interval: int = 5) -> bool:
        """
        Waits for a Textract job to complete by polling its status.
        
        :param job_id: The Textract job ID.
        :param poll_interval: Seconds to wait between status checks (default: 5).
        :return: True if the job succeeded, raises exception if it failed.
        """
        while True:
            try:
                resp = self.textract_client.get_document_text_detection(JobId=job_id)
                status = resp["JobStatus"]
                logger.info(f"Textract job {job_id} status: {status}")
                
                if status == "SUCCEEDED":
                    return True
                if status == "FAILED":
                    error_message = resp.get("StatusMessage", "Unknown error")
                    raise Exception(f"Textract job {job_id} failed: {error_message}")
                
                time.sleep(poll_interval)
            except ClientError:
                logger.exception(f"Error checking status of job {job_id}")
                raise

    def get_all_results(self, job_id: str) -> list[dict]:
        """
        Retrieves all paginated results from a completed Textract job.
        
        :param job_id: The Textract job ID.
        :return: List of response pages containing all blocks.
        """
        pages = []
        next_token = None
        
        try:
            while True:
                if next_token:
                    resp = self.textract_client.get_document_text_detection(
                        JobId=job_id,
                        NextToken=next_token
                    )
                else:
                    resp = self.textract_client.get_document_text_detection(JobId=job_id)
                
                pages.append(resp)
                
                next_token = resp.get("NextToken")
                if not next_token:
                    break
            
            total_blocks = sum(len(page.get("Blocks", [])) for page in pages)
            logger.info(f"Retrieved {len(pages)} pages with {total_blocks} total blocks for job {job_id}")
            return pages
        except ClientError:
            logger.exception(f"Error retrieving results for job {job_id}")
            raise

    def extract_text_from_results(self, results: list[dict]) -> str:
        """
        Extracts plain text from Textract results by concatenating LINE blocks.
        
        :param results: List of Textract response pages (from get_all_results).
        :return: Plain text extracted from the document, with lines separated by newlines.
        """
        texto = []
        
        for page in results:
            blocks = page.get("Blocks", [])
            for block in blocks:
                if block.get("BlockType") == "LINE":
                    texto.append(block.get("Text", ""))
        
        texto_final = "\n".join(texto)
        logger.info(f"Extracted {len(texto)} lines of text from {len(results)} pages")
        return texto_final

    def detect_document_text_from_s3(
        self, 
        bucket: str, 
        document_key: str, 
        poll_interval: int = 5,
        return_raw_results: bool = False
    ) -> str | list[dict]:
        """
        Complete workflow to detect text from a document in S3.
        Starts the job, waits for completion, retrieves all results, and extracts text.
        
        :param bucket: The S3 bucket name.
        :param document_key: The S3 object key (path) of the document.
        :param poll_interval: Seconds to wait between status checks (default: 5).
        :param return_raw_results: If True, returns raw results instead of extracted text.
        :return: Extracted plain text (default) or list of raw result pages if return_raw_results=True.
        """
        workflow_start = time.time()
        logger.info(f"🔍 [Textract] Iniciando workflow completo para s3://{bucket}/{document_key}")
        logger.info(f"🔍 [Textract] Parámetros: poll_interval={poll_interval}s, return_raw_results={return_raw_results}")
        
        try:
            # Step 1: Start the job
            logger.info(f"🔍 [Textract] Paso 1/4: Iniciando job de detección de texto...")
            start_job_start = time.time()
            job_id = self.start_document_text_detection_from_s3(bucket, document_key)
            start_job_time = time.time() - start_job_start
            logger.info(f"🔍 [Textract] Paso 1/4 completado: Job iniciado con ID {job_id} en {start_job_time:.4f}s")
            
            # Step 2: Wait for completion
            logger.info(f"🔍 [Textract] Paso 2/4: Esperando completación del job (polling cada {poll_interval}s)...")
            wait_start = time.time()
            self.wait_for_completion(job_id, poll_interval)
            wait_time = time.time() - wait_start
            logger.info(f"🔍 [Textract] Paso 2/4 completado: Job finalizado exitosamente en {wait_time:.4f}s")
            
            # Step 3: Get all results
            logger.info(f"🔍 [Textract] Paso 3/4: Obteniendo todos los resultados paginados...")
            get_results_start = time.time()
            results = self.get_all_results(job_id)
            get_results_time = time.time() - get_results_start
            total_pages = len(results)
            total_blocks = sum(len(page.get("Blocks", [])) for page in results)
            logger.info(f"🔍 [Textract] Paso 3/4 completado: {total_pages} páginas con {total_blocks} bloques totales obtenidos en {get_results_time:.4f}s")
            
            # Step 4: Extract text or return raw results
            if return_raw_results:
                workflow_time = time.time() - workflow_start
                logger.info(f"🔍 [Textract] Paso 4/4: Retornando resultados raw (solicitado por usuario)")
                logger.info(f"🔍 [Textract] ⏱️  TIEMPO TOTAL TEXTRACT: {workflow_time:.4f}s")
                logger.info(f"✅ [Textract] Workflow completo finalizado en {workflow_time:.4f}s")
                return results
            
            logger.info(f"🔍 [Textract] Paso 4/4: Extrayendo texto plano de los resultados...")
            extract_start = time.time()
            texto_final = self.extract_text_from_results(results)
            extract_time = time.time() - extract_start
            texto_lines = len(texto_final.split("\n")) if texto_final else 0
            texto_chars = len(texto_final) if texto_final else 0
            logger.info(f"🔍 [Textract] Paso 4/4 completado: {texto_lines} líneas ({texto_chars} caracteres) extraídos en {extract_time:.4f}s")
            
            workflow_time = time.time() - workflow_start
            logger.info(f"🔍 [Textract] ⏱️  TIEMPO TOTAL TEXTRACT: {workflow_time:.4f}s")
            logger.info(f"✅ [Textract] Workflow completo finalizado exitosamente en {workflow_time:.4f}s")
            logger.info(f"📊 [Textract] Resumen: {total_pages} páginas → {texto_lines} líneas de texto")
            
            return texto_final
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            workflow_time = time.time() - workflow_start
            logger.error(f"❌ [Textract] Error de AWS después de {workflow_time:.4f}s: {error_code}: {error_message}")
            logger.error(f"❌ [Textract] Documento: s3://{bucket}/{document_key}")
            raise
        except Exception as e:
            workflow_time = time.time() - workflow_start
            logger.error(f"❌ [Textract] Error inesperado después de {workflow_time:.4f}s: {type(e).__name__}: {e}")
            logger.error(f"❌ [Textract] Documento: s3://{bucket}/{document_key}")
            raise
