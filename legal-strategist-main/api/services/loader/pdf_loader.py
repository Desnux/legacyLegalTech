import logging
import ocrmypdf
import os
import pikepdf
import pypdfium2
import subprocess
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from typing import Iterator

from langchain_community.document_loaders import PyPDFium2Loader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class PdfLoader(BaseLoader):
    """Transforms PDF files into langchain Documents."""
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        loader = PyPDFium2Loader(self.file_path, extract_images=True)
        return loader.lazy_load()
    
    def load(self) -> list[Document]:
        return list(self.parse(self.file_path))
    
    def load_no_ocr(self) -> list[Document]:
        loader = PyPDFium2Loader(self.file_path, extract_images=False)
        return list(loader.lazy_load())

    def parse(self, file_path: str) -> Iterator[Document]:
        repaired_pdf_path = None
        try:
            with pikepdf.open(file_path) as pdf:
                pass
        except pikepdf.PdfError as e:
            logging.warning(f"PDF is corrupted: {e}. Attempting to repair...")
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as repaired_pdf:
                repaired_pdf_path = repaired_pdf.name
                success = self.repair_pdf_with_ghostscript(file_path, repaired_pdf_path)
            if success:
                logging.info("PDF repaired successfully with Ghostscript.")
                file_path = repaired_pdf_path
            else:
                logging.warning("Ghostscript repair failed. Attempting to repair with pikepdf...")
                try:
                    with pikepdf.open(file_path) as pdf:
                        pdf.save(repaired_pdf_path)
                    logging.info("PDF repaired successfully with pikepdf.")
                    file_path = repaired_pdf_path
                except pikepdf.PdfError as repair_error:
                    logging.error(f"Failed to repair PDF with pikepdf: {repair_error}")
                    raise
        
        pdf_reader = pypdfium2.PdfDocument(file_path, autoclose=True)
        ocr_output_pdf_path = None
        pages_to_process = set()
        results = {}

        for page_number, page in enumerate(pdf_reader):
            text_page = page.get_textpage()
            content = text_page.get_text_range(force_this=True).strip()
            text_page.close()
            page.close()
            if not content:
                pages_to_process.add(page_number)
            else:
                results[page_number] = Document(page_content=content, metadata={"source": file_path, "page": page_number})

        if pages_to_process:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as ocr_output_pdf:
                ocr_output_pdf_path = ocr_output_pdf.name
            with open(os.devnull, "w") as fnull:
                with redirect_stdout(fnull), redirect_stderr(fnull):
                    logging.info(f"PDF processing with ocrmypdf")
                    ocrmypdf.ocr(
                        file_path,
                        ocr_output_pdf_path,
                        use_threads=False,
                        language="spa",
                        force_ocr=True,
                        invalidate_digital_signatures=True,
                        output_type="pdf",
                    )
        
        for page_number in pages_to_process:
            page = pdf_reader[page_number]
            doc = self.process_page(page_number, page, file_path, ocr_output_pdf_path)
            results[page_number] = doc
        
        for page_number in sorted(results.keys()):
            yield results[page_number]

        pdf_reader.close()
        if ocr_output_pdf_path and os.path.exists(ocr_output_pdf_path):
            os.remove(ocr_output_pdf_path)

    def process_page(self, page_number: int, page: pypdfium2.PdfPage, file_path: str, ocr_output_pdf_path: str) -> Document:
        """Extracts text from a given PDF page, applying OCR if necessary. """
        text_page = page.get_textpage()
        content = text_page.get_text_range(force_this=True).strip()
        text_page.close()
        page.close()
        if not content and ocr_output_pdf_path:
            with open(ocr_output_pdf_path, "rb") as f:
                ocr_pdf_reader = pypdfium2.PdfDocument(f)
                ocr_page = ocr_pdf_reader[page_number]
                ocr_text_page = ocr_page.get_textpage()
                content = ocr_text_page.get_text_range(force_this=True).strip()
                ocr_text_page.close()
                ocr_page.close()
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
