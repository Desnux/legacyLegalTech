import logging
import ocrmypdf
import os
import pikepdf
import pypdfium2
import subprocess
import sys
import tempfile
import time
import traceback
import threading
import uuid
from typing import Iterator

from langchain_community.document_loaders import PyPDFium2Loader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from storage import S3Storage, TextractWrapper


# Lock global para sincronizar operaciones de pypdfium2
# pypdfium2/libpdfium NO es thread-safe, especialmente en destructores de objetos CPDF_Color
# Ver: https://pypdfium2-team.github.io/pypdfium2/python_api.html
# "PDFium no es inherentemente seguro para hilos. No está permitido llamar a funciones 
# de pdfium simultáneamente en diferentes hilos, ni siquiera con diferentes documentos."
_pypdfium2_lock = threading.Lock()



class DevNullWrapper:
    """Wrapper que simula un archivo siempre abierto para evitar errores de rich"""
    def __init__(self):
        self._file = open(os.devnull, "w")
    
    @property
    def closed(self):
        """Siempre reporta que está abierto para que rich pueda escribir"""
        return False
    
    def write(self, text):
        """Escribe a /dev/null, siempre funciona"""
        try:
            self._file.write(text)
        except (ValueError, OSError):
            pass  # Ignorar errores de escritura
    
    def flush(self):
        """Flush a /dev/null"""
        try:
            self._file.flush()
        except (ValueError, OSError):
            pass
    
    def close(self):
        """No hace nada, mantiene el archivo abierto para que rich pueda escribir"""
        pass  # NO cerrar realmente el archivo
    
    def readable(self):
        """Reporta que es legible"""
        return False
    
    def writable(self):
        """Reporta que es escribible"""
        return True
    
    def seekable(self):
        """Reporta que no es seekable"""
        return False
    
    def __getattr__(self, name):
        """Delegar otros atributos al archivo real"""
        return getattr(self._file, name)
    
    def __del__(self):
        """Cerrar el archivo solo cuando se destruye el objeto"""
        try:
            if hasattr(self, '_file') and not self._file.closed:
                self._file.close()
        except:
            pass


def is_text_usable(text: str) -> bool:
    """
    Determina si el texto extraído es suficiente para evitar OCR.
    """
    if not text:
        return False

    text = text.strip()
    if len(text) < 500:
        return False

    letters = sum(c.isalpha() for c in text)
    ratio = letters / max(len(text), 1)

    return ratio > 0.6


def calculate_textract_confidence(blocks: list[dict]) -> float:
    """
    Calcula la confianza promedio de Textract basada en bloques LINE.
    """
    confidences = [
        block.get("Confidence", 0.0)
        for block in blocks
        if block.get("BlockType") == "LINE"
    ]

    if not confidences:
        return 0.0

    return round(sum(confidences) / len(confidences), 2)


def mask_low_confidence_text(text: str, confidence: float, threshold: float = 85.0) -> str:
    """
    Si la confianza es menor al umbral, reemplaza el contenido por 'XXXXXX'.
    """
    if confidence < threshold:
        return "XXXXXX"
    return text


class PdfLoader(BaseLoader):
    """Transforms PDF files into langchain Documents."""
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._textract_time: float = 0.0  # Store Textract processing time

    def lazy_load(self) -> Iterator[Document]:
        loader = PyPDFium2Loader(self.file_path, extract_images=True)
        return loader.lazy_load()
    
    def load(self) -> list[Document]:
        thread_id = threading.current_thread().ident
        logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] load() llamado para: {self.file_path}")

        # 1️⃣ Intentar texto nativo (rápido, confiable)
        try:
            native_loader = PyPDFium2Loader(self.file_path, extract_images=False)
            native_docs = list(native_loader.lazy_load())
            native_text = "\n".join(d.page_content for d in native_docs if d.page_content)

            if is_text_usable(native_text):
                logging.info(f"  ✅ [PdfLoader] Texto nativo usable detectado. OCR omitido.")
                for doc in native_docs:
                    doc.metadata["extraction_method"] = "NATIVE_PDF"
                    doc.metadata["confidence"] = 98.0
                return native_docs

            logging.info(f"  ⚠️ [PdfLoader] Texto nativo insuficiente. Se usará Textract.")

        except Exception as e:
            logging.warning(
                f"  ⚠️ [PdfLoader] Error leyendo texto nativo, fallback a Textract: {e}"
            )

        # 2️⃣ Fallback a Textract (pipeline existente)
        documents = list(self.parse(self.file_path))
        return documents

    
    @property
    def textract_time(self) -> float:
        """
        Get the Textract processing time from the last parse operation.
        
        Returns:
            float: Time spent in Textract processing (upload, job execution, result retrieval), in seconds
        """
        return self._textract_time
    
    def load_no_ocr(self) -> list[Document]:
        loader = PyPDFium2Loader(self.file_path, extract_images=False)
        return list(loader.lazy_load())

    def parse(self, file_path: str) -> Iterator[Document]:
        """
        Parse PDF using Amazon Textract async method via S3.
        Uploads PDF to S3, processes with Textract, and extracts text.
        """
        thread_id = threading.current_thread().ident
        logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Iniciando parse() con Textract (método asíncrono) para: {file_path}")
        
        s3_storage = None
        textract_wrapper = None
        s3_key = None
        
        try:
            # Step 1: Read PDF file
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Leyendo archivo PDF...")
            read_start = time.time()
            with open(file_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            read_time = time.time() - read_start
            file_size_mb = len(pdf_data) / (1024 * 1024)
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Archivo leído: {file_size_mb:.2f} MB en {read_time:.4f}s")
            
            # Step 2: Upload PDF to S3
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Subiendo PDF a S3...")
            s3_storage = S3Storage()
            textract_wrapper = TextractWrapper()
            
            # Generate unique S3 key for this PDF
            s3_key = f"textract-temp/{uuid.uuid4()}.pdf"
            
            upload_start = time.time()
            s3_storage.save(s3_key, pdf_data)
            upload_time = time.time() - upload_start
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] PDF subido a S3: s3://{s3_storage.bucket}/{s3_key} en {upload_time:.4f}s")
            
            # Step 3: Extract text using Textract async method
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Iniciando extracción de texto con Textract (método asíncrono)...")
            textract_start = time.time()
            raw_results = textract_wrapper.detect_document_text_from_s3(
                bucket=s3_storage.bucket,
                document_key=s3_key,
                poll_interval=5,
                return_raw_results=True
            )
            self._textract_time = round(time.time() - textract_start, 4)
            logging.info(f"  🔍 [Textract] Tiempo total de procesamiento: {self._textract_time:.4f}s")
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Textract completado en {self._textract_time:.4f}s")
            
            # Step 4: Convert extracted text to LangChain Documents by page
            # Extract blocks from all pages
            blocks = []
            for page_result in raw_results:
                blocks.extend(page_result.get("Blocks", []))
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Procesando {len(blocks)} bloques de Textract...")
            
            if blocks:
                # Dictionary to store text per page: {page_number: [lines]}
                pages_text = {}
                
                for block in blocks:
                    if block.get("BlockType") == "LINE":
                        page_num = block.get("Page", 1) - 1  # Convert to 0-based index
                        if page_num not in pages_text:
                            pages_text[page_num] = []
                        pages_text[page_num].append(block.get("Text", ""))
                
                # Create Document for each page
                if pages_text:
                    confidence = calculate_textract_confidence(blocks)
                    logging.info(f"  🔍 [Textract] Confianza promedio OCR: {confidence}%")
                    for page_number in sorted(pages_text.keys()):
                        page_text = "\n".join(pages_text[page_number])
                        if page_text.strip():  # Only yield non-empty pages
                            safe_text = mask_low_confidence_text(page_text.strip(), confidence)
                            yield Document(
                                page_content=safe_text,
                                metadata={
                                    "source": file_path,
                                    "page": page_number,
                                    "extraction_method": "OCR_TEXTRACT",
                                    "confidence": confidence
                                })
                            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Página {page_number + 1} procesada: {len(page_text)} caracteres")
                    logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Total de páginas procesadas: {len(pages_text)}")
                else:
                    logging.warning(f"  📄 [PdfLoader] [Thread {thread_id}] No se encontraron bloques de texto LINE en los resultados")
                    # Yield empty document to maintain consistency
                    yield Document(
                        page_content="",
                        metadata={"source": file_path, "page": 0}
                    )
            else:
                logging.warning(f"  📄 [PdfLoader] [Thread {thread_id}] No se extrajo texto del PDF (respuesta vacía o sin bloques)")
                # Yield empty document to maintain consistency
                yield Document(
                    page_content="",
                    metadata={"source": file_path, "page": 0}
                )
            
            logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] parse() completado exitosamente")
            
        except Exception as e:
            logging.error(f"  ❌ [PdfLoader] [Thread {thread_id}] Error en parse() con Textract: {type(e).__name__}: {e}")
            logging.error(f"  📋 [PdfLoader] Stack trace: {traceback.format_exc()}")
            raise
        finally:
            # Cleanup: Delete PDF from S3
            if s3_storage and s3_key:
                try:
                    s3_storage.delete(s3_key)
                    logging.info(f"  📄 [PdfLoader] [Thread {thread_id}] Archivo temporal eliminado de S3: {s3_key}")
                except Exception as cleanup_error:
                    logging.warning(f"  ⚠️ [PdfLoader] [Thread {thread_id}] Error eliminando archivo temporal de S3: {cleanup_error}")

    def process_page(self, page_number: int, page: pypdfium2.PdfPage, file_path: str, ocr_output_pdf_path: str) -> Document:
        """Extracts text from a given PDF page, applying OCR if necessary. 
        
        NOTA: Este método ya no se usa en el flujo principal, pero se mantiene por compatibilidad.
        El procesamiento de OCR ahora se hace directamente en parse() con el lock apropiado.
        """
        text_page = page.get_textpage()
        content = text_page.get_text_range(force_this=True).strip()
        text_page.close()
        page.close()
        if not content and ocr_output_pdf_path:
            # Este código ya no debería ejecutarse, pero si lo hace, necesita el lock
            with _pypdfium2_lock:
                with open(ocr_output_pdf_path, "rb") as f:
                    ocr_pdf_reader = pypdfium2.PdfDocument(f)
                    ocr_page = ocr_pdf_reader[page_number]
                    ocr_text_page = ocr_page.get_textpage()
                    content = ocr_text_page.get_text_range(force_this=True).strip()
                    ocr_text_page.close()
                    ocr_page.close()
                    ocr_pdf_reader.close()
        metadata = {"source": file_path, "page": page_number}
        return Document(page_content=content, metadata=metadata)

    def repair_pdf_with_ghostscript(self, input_pdf_path: str, output_pdf_path: str) -> bool:
        """Repairs corrupted PDF files with Ghostscript."""
        try:
            subprocess.run(
                [
                    "gs", 
                    "-o", output_pdf_path, 
                    "-sDEVICE=pdfwrite", 
                    "-dPDFSETTINGS=/prepress", 
                    "-dNOPAUSE", 
                    "-dBATCH", 
                    input_pdf_path
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logging.info(f"Ghostscript repair completed")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Ghostscript repair failed: {e}")
            return False
