import logging
import time
from fastapi import File, Form, UploadFile

from models.api import error_response
from models.pydantic import MissingPaymentDocumentType, MissingPaymentFile
from services.v2.document.demand_text.input import (
    DemandTextInputExtractor,
    DemandTextInputExtractorInput,
    DemandTextInputExtractorOutput,
)
from . import router


@router.post("/demand-text-input/", response_model=DemandTextInputExtractorOutput)
async def demand_text_input_post(
    text: str = Form(..., description="Demand text input raw text", max_length=32768),
    file_types: list[MissingPaymentDocumentType] = Form([], description="File types", max_length=10),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
):
    """Handles the extraction of a demand text input from a string and PDF files."""

    total_start_time = time.time()
    
    validation_start = time.time()
    document_files: list[MissingPaymentFile] = []
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            return error_response("Invalid file type", 400)
        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))
    validation_time = time.time() - validation_start
    logging.info(f"📋 [ETAPA 1] Validación de archivos: {validation_time:.4f}s")

    try:
        extractor_creation_start = time.time()
        demand_text_input_extractor = DemandTextInputExtractor(DemandTextInputExtractorInput(
            files=document_files,
            text=text,
        ))
        extractor_creation_time = time.time() - extractor_creation_start
        logging.info(f"⚙️  [ETAPA 2] Creación del extractor: {extractor_creation_time:.4f}s")
        
        extraction_start = time.time()
        information = demand_text_input_extractor.extract()
        extraction_time = time.time() - extraction_start
        logging.info(f"🔍 [ETAPA 3] Extracción de información: {extraction_time:.4f}s")
        
        total_time = time.time() - total_start_time
        logging.info(f"⏱️  [TOTAL] Tiempo total del endpoint: {total_time:.4f}s")
        
        if information and information.metrics:
            logging.info(f"🤖 [OPENAI] Invocaciones totales: {information.metrics.llm_invocations}")
            logging.info(f"🤖 [OPENAI] Tiempo total de procesamiento: {information.metrics.time:.4f}s")
            if information.metrics.submetrics:
                for i, submetric in enumerate(information.metrics.submetrics):
                    logging.info(f"📄 [DOCUMENTO {i+1}] Tiempo: {submetric.time:.4f}s | Llamadas OpenAI: {submetric.llm_invocations}")
        
        logging.info("=" * 80)
        logging.info("📊 RESUMEN DE RENDIMIENTO - ENDPOINT /v1/extract/demand-text-input/")
        logging.info("=" * 80)
        
        logging.info(f"📋 [ETAPA 1] Validación de archivos:     {validation_time:.4f}s")
        logging.info(f"⚙️  [ETAPA 2] Creación del extractor:     {extractor_creation_time:.4f}s")
        logging.info(f"🔍 [ETAPA 3] Extracción de información:   {extraction_time:.4f}s")
        logging.info("-" * 80)
        logging.info(f"⏱️  [TOTAL] Tiempo total del endpoint:     {total_time:.4f}s")
        
        if information and information.metrics:
            logging.info(f"🤖 [OPENAI] Tiempo de procesamiento LLM: {information.metrics.time:.4f}s")
            logging.info(f"🤖 [OPENAI] Total de invocaciones:        {information.metrics.llm_invocations}")
            logging.info("-" * 80)
            logging.info("🔍 DETALLE DE INVOCACIONES OPENAI:")
            
            text_invocations = 0
            pdf_invocations = sum(submetric.llm_invocations for submetric in information.metrics.submetrics) if information.metrics.submetrics else 0
            merge_invocations = information.metrics.llm_invocations - text_invocations - pdf_invocations
            
            if information.metrics.text_processing_time and information.metrics.text_processing_time > 0:
                logging.info(f"   📝 Procesamiento de texto: {information.metrics.text_processing_time:.4f}s (0 llamadas - solo parseo JSON local)")
            
            if information.metrics.submetrics:
                real_pdf_time = max(submetric.time for submetric in information.metrics.submetrics)
                logging.info(f"   📄 Procesamiento PDFs total: {real_pdf_time:.4f}s ({pdf_invocations} llamadas) - procesados en paralelo")
                for i, submetric in enumerate(information.metrics.submetrics):
                    # Show Textract time
                    textract_info = f" | Textract: {submetric.textract_time:.4f}s" if submetric.textract_time > 0 else ""
                    # Show individual OpenAI times (limit to first 5 for readability)
                    openai_times_str = ""
                    if submetric.openai_times:
                        max_times_to_show = 5
                        times_to_show = submetric.openai_times[:max_times_to_show]
                        times_list = ", ".join([f"{t:.4f}s" for t in times_to_show])
                        if len(submetric.openai_times) > max_times_to_show:
                            times_list += f", ... ({len(submetric.openai_times) - max_times_to_show} más)"
                        openai_times_str = f" | OpenAI: [{times_list}]"
                    logging.info(f"      └─ Documento {i+1}: {submetric.time:.4f}s ({submetric.llm_invocations} llamadas){textract_info}{openai_times_str}")
            
            if merge_invocations > 0:
                logging.info(f"   🔄 Merge de información: {information.metrics.merge_processing_time:.4f}s ({merge_invocations} llamadas)")
        
        logging.info("=" * 80)
        
    except Exception as e:
        total_time = time.time() - total_start_time
        logging.error(f"Error after {total_time:.4f}s: {e}")
        return error_response(f"Could not extract information from input: {e}", 500)
    
    return information
