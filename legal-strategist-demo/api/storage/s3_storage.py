import logging
from collections.abc import Generator
from contextlib import closing
from urllib.parse import quote

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from config import Config
from .base_storage import BaseStorage


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
    
    def save(self, filename: str, data) -> None:
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
