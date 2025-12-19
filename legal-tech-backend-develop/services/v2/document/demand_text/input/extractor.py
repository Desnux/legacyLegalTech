import logging
import json
import os
import shutil
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

from models.pydantic import (
    CurrencyType,
    Defendant,
    DefendantType,
    MissingPaymentDocumentType,
    MissingPaymentFile,
    Plaintiff,
    LegalSubject,
)
from services.v2.document.base import BaseExtractor, Metrics
from services.v2.document.bill import (
    BillExtractor,
    BillExtractorInput,
    BillExtractorOutput,
    BillInformation,
)
from services.v2.document.demand_text.missing_payment_argument import (
    MissingPaymentArgumentReason,
)
from services.v2.document.promissory_note import (
    PromissoryNoteExtractor,
    PromissoryNoteExtractorInput,
    PromissoryNoteExtractorOutput,
    PromissoryNoteInformation,
)
from .models import (
    DemandTextInputExtractorInput,
    DemandTextInputExtractorOutput,
    DemandTextInputInformation,
    DemandTextInputPartialInformation,
    DemandTextUniqueLitigants,
)


USD_TO_CLP_EXCHANGE = 1000


class DemandTextInputExtractor(BaseExtractor):
    """Demand text input extractor."""

    def __init__(self, input: DemandTextInputExtractorInput) -> None:
        super().__init__()
        self.input = input
        self.extractor = self._create_structured_extractor(DemandTextInputPartialInformation)
        self.merger = self._create_structured_extractor(DemandTextUniqueLitigants)

    def extract(self) -> DemandTextInputExtractorOutput:
        """Extract structured information from input."""
        information = DemandTextInputInformation()
        metrics = Metrics(label=f"DemandTextInputExtractor.extract", submetrics=[])
        start_time = time.time()
        
        # Variables para almacenar tiempos de invocaciones
        text_processing_time = 0.0
        merge_processing_time = 0.0

        # Etapa 1: Procesamiento de texto de entrada
        if source := self.input.text:
            text_processing_start = time.time()
            logging.info("📝 [SUBPROCESO] Iniciando procesamiento de texto...")
            payload = json.loads(source)
            # Transformar estructura: extraer campos de 'participants' al nivel raíz
            if "participants" in payload and isinstance(payload["participants"], dict):
                participants = payload.pop("participants")
                if "plaintiff" in participants:
                    payload["plaintiff"] = participants["plaintiff"]
                if "legal_representatives" in participants:
                    payload["legal_representatives"] = participants["legal_representatives"]
                if "sponsoring_attorneys" in participants:
                    payload["sponsoring_attorneys"] = participants["sponsoring_attorneys"]
            information = DemandTextInputInformation.model_validate(payload)
            information.normalize()
            logging.info(f"📝 [SUBPROCESO] Información transformada: {information.model_dump_json()}")
            logging.info("✅ [SUBPROCESO] JSON parseado y validado correctamente")
            text_processing_time = time.time() - text_processing_start
            logging.info(f"📝 [SUBPROCESO] Procesamiento de texto completado: {text_processing_time:.4f}s")
        
        # Etapa 2: Procesamiento de documentos PDF
        pdf_processing_start = time.time()
        logging.info("📄 [SUBPROCESO] Iniciando procesamiento de PDFs...")
        documents, document_types = self._extract_documents()
        pdf_processing_time = time.time() - pdf_processing_start
        logging.info(f"📄 [SUBPROCESO] Procesamiento de PDFs completado: {pdf_processing_time:.4f}s")
        
        reasons = information.reasons_per_document or []
        final_documents: list[BillInformation | PromissoryNoteInformation] = []
        final_document_types: list[MissingPaymentDocumentType] = []
        final_reasons: list[MissingPaymentArgumentReason] = []
        if len(documents) != len(reasons):
            logging.warning(f"Mismatch between files {len(documents)} and provided reasons to argue {len(reasons)}.")
        
        if information.amount is None:
            information.amount = 0
        elif information.amount < 0:
            information.amount = 0
        update_amount = information.amount == 0
        if information.creditors is None:
            information.creditors = []
        if information.defendants is None:
            information.defendants = []

        for document, document_type, reason in zip(documents, document_types, reasons):
            if not document:
                continue
            if not document_type:
                continue
            if document_metrics := document.metrics:
                metrics.llm_invocations += document_metrics.llm_invocations
                metrics.submetrics.append(document_metrics)
            if document_output := document.structured_output:
                final_documents.append(document.structured_output)
                final_document_types.append(document_type)
                final_reasons.append(reason)

                if reason_amount := reason.pending_amount:
                    document_amount = reason_amount
                else:
                    document_amount = document_output.amount or 0
                if currency := document_output.amount_currency:
                    if not information.amount_currency:
                        information.amount_currency = currency
                    elif information.amount_currency == CurrencyType.CLP and currency == CurrencyType.USD:
                        document_amount *= USD_TO_CLP_EXCHANGE
                if update_amount:
                    information.amount += document_amount

                if city := document_output.city:
                    if not information.city:
                        information.city = city
                for debtor in document_output.debtors or []:
                    information.defendants.append(Defendant(
                        name=debtor.name,
                        identifier=debtor.identifier,
                        occupation=debtor.occupation,
                        address=debtor.address,
                        legal_representatives=debtor.legal_representatives,
                        type=DefendantType.DEBTOR,
                    ))
                if document_type == MissingPaymentDocumentType.PROMISSORY_NOTE:
                    for debtor in document_output.co_debtors or []:
                        information.defendants.append(Defendant(
                            name=debtor.name,
                            identifier=debtor.identifier,
                            occupation=debtor.occupation,
                            address=debtor.address,
                            legal_representatives=debtor.legal_representatives,
                            type=DefendantType.CO_DEBTOR,
                        ))
                information.creditors.extend(document_output.creditors or [])
        
        # Etapa 3: Merge de información (si hay duplicados)
        merge_information = len(information.creditors) > 1
        merge_information |= len(information.defendants) > 1
        merge_information |= len(information.sponsoring_attorneys or []) > 1
        if merge_information:
            merge_start = time.time()
            logging.info("🔄 [SUBPROCESO] Iniciando merge de información...")
            self._merge_information(information)
            metrics.llm_invocations += 1
            merge_processing_time = time.time() - merge_start
            logging.info(f"🔄 [SUBPROCESO] Merge de información completado: {merge_processing_time:.4f}s")

        information.documents = final_documents
        information.document_types = final_document_types
        information.reasons_per_document = final_reasons
        if len(information.creditors) > 0 and not information.plaintiff:
            information.plaintiff = Plaintiff(
                name=information.creditors[0].name,
                identifier=information.creditors[0].identifier,
                address=information.creditors[0].address,
            )
        if not information.document_types:
            information.legal_subject = LegalSubject.GENERAL_COLLECTION
        if all(map(lambda x: x == MissingPaymentDocumentType.PROMISSORY_NOTE, information.document_types)):
            information.legal_subject = LegalSubject.PROMISSORY_NOTE_COLLECTION
        elif all(map(lambda x: x == MissingPaymentDocumentType.BILL, information.document_types)):
            information.legal_subject = LegalSubject.BILL_COLLECTION
        else:
            information.legal_subject = LegalSubject.GENERAL_COLLECTION
        information.normalize()

        metrics.time = round(time.time() - start_time, 4)
        metrics.text_processing_time = round(text_processing_time, 4)
        metrics.merge_processing_time = round(merge_processing_time, 4)
        return DemandTextInputExtractorOutput(metrics=metrics, structured_output=information)
    
    def _create_prompt(self, source: str) -> str:
        prompt = f"""
        Your task is to extract information necessary to write a demand text about missing payments from the following source object. The source contains key-value pairs with information written by an attorney in English:
        <source>{source}</source>

        When extracting information:
        - Do not use fake or example data, only use information provided inside source tags.
        - If an attribute is missing, you may assign is value as None or an equivalent value.
        - Transform uppercase or lowercase words into most common casing for each kind of string value, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - For reasons_per_document: Preserve ALL reasons exactly as provided, even if they are duplicates. Do not consolidate or merge them.
        - For sponsoring attorneys:
            - Look for keys/values related to lawyers who are signing or sponsoring the demand text
            - Common keys may include "sponsoring_attorney", "attorney", "lawyer", etc.
            - Extract their full name, identifier number, and address
            - Pay special attention to fields indicating they are acting as sponsoring attorneys
        - For legal representatives:
            - Look for keys/values identifying persons who are explicitly mentioned as representing or acting on behalf of another party
            - Common keys may include "legal_representative", "representative", "proxy", etc.
            - Extract their full name, identifier number, occupation, and address
            - Pay special attention to fields indicating they have legal representation powers
        """
        return prompt

    def _extract_documents(self) -> tuple[list[BillExtractorOutput | PromissoryNoteExtractorOutput | None], list[MissingPaymentDocumentType | None]]:
        documents: list[BillExtractorOutput | PromissoryNoteExtractorOutput | None] = []
        document_types: list[MissingPaymentDocumentType | None] = []
        if not self.input.files:
            return documents, document_types
        
        max_workers = min(len(self.input.files), 5)
        logging.info(f"📄 [ARCHIVOS] Procesando {len(self.input.files)} archivos con {max_workers} workers en paralelo")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}
            for idx, file in enumerate(self.input.files):
                future = executor.submit(self._process_file, file, idx)
                future_to_file[future] = (idx, file)

            results = [None] * len(self.input.files)
            doc_types = [None] * len(self.input.files)
            
            for future in as_completed(future_to_file):
                idx, file = future_to_file[future]
                filename = file.upload_file.filename if file.upload_file else f"file_{idx+1}.pdf"
                try:
                    _, document, document_type = future.result(timeout=600)
                    results[idx] = document
                    doc_types[idx] = document_type
                except TimeoutError:
                    logging.error(f"⏱️  [ARCHIVO {idx+1}] Timeout procesando {filename} (más de 10 minutos)")
                    results[idx] = None
                    doc_types[idx] = None
                except Exception as e:
                    logging.error(f"❌ [ARCHIVO {idx+1}] Error procesando {filename}: {type(e).__name__}: {e}")
                    logging.error(f"  📋 Stack trace: {traceback.format_exc()}")
                    results[idx] = None
                    doc_types[idx] = None
        
        documents = results
        document_types = doc_types
        successful_count = sum(1 for d in documents if d is not None)
        logging.info(f"📄 [ARCHIVOS] Procesamiento completado: {successful_count}/{len(self.input.files)} archivos procesados exitosamente")
        
        return documents, document_types

    def _process_file(self, file: MissingPaymentFile, index: int) -> tuple[
        int,
        BillExtractorOutput | PromissoryNoteExtractorOutput | None,
        MissingPaymentDocumentType | None
    ]:
        if file.document_type not in [MissingPaymentDocumentType.BILL, MissingPaymentDocumentType.PROMISSORY_NOTE]:
            return index, None, None
        if file.upload_file is None:
            return index, None, None

        temp_file_path = None
        document: BillExtractorOutput | PromissoryNoteExtractorOutput | None = None

        try:
            file_start = time.time()
            filename = file.upload_file.filename if file.upload_file else f"file_{index+1}.pdf"
            
            file.upload_file.file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                shutil.copyfileobj(file.upload_file.file, temp_file)
                temp_file_path = temp_file.name

            if file.document_type == MissingPaymentDocumentType.PROMISSORY_NOTE:
                extractor = PromissoryNoteExtractor(PromissoryNoteExtractorInput(file_path=temp_file_path))
                document = extractor.extract()
            elif file.document_type == MissingPaymentDocumentType.BILL:
                extractor = BillExtractor(BillExtractorInput(file_path=temp_file_path))
                document = extractor.extract()
            
            file_time = time.time() - file_start
            logging.info(f"✅ [ARCHIVO {index+1}] Procesamiento completado en {file_time:.4f}s: {filename}")
                
        except Exception as e:
            filename = file.upload_file.filename if file.upload_file else f"file_{index+1}.pdf"
            logging.error(f"❌ [ARCHIVO {index+1}] Error procesando documento {filename}: {type(e).__name__}: {e}")
            logging.error(f"  📋 Stack trace: {traceback.format_exc()}")
            return index, None, None
        finally:
            if temp_file_path is not None and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
    
        return index, document, file.document_type

    def _merge_information(self, information: DemandTextInputInformation) -> None:
        
        prompt = """
        For each kind of role (creditor, defendant, or sponsoring attorney), if the list of associated values is bigger than 1,
        your task is to ensure that each role list contains only unique entities, either by removing repeated entities, or merging similar entities into one.

        Criteria for mixing information:
        - A defendant can also be a legal representative of one or more defendants.
        - There cannot be repeated legal representatives for the same defendant.
        - You may cross-reference between defendants and legal representatives to add missing information or help you decide to remove or merge entities, for example,
        if Juanito Lopez appears as both a defendant and a legal representative, but lacks an identifier as a defendant, you should assing him his legal representative identifier in both.
        - IMPORTANT: For defendants, when a co_debtor (aval) and a legal_representative have the same identifier but different address information, complement the missing address:
          * If the co_debtor has an address but the legal_representative doesn't, use the co_debtor's address for the legal_representative.
          * If the legal_representative has an address but the co_debtor doesn't, use the legal_representative's address for the co_debtor.
          * This ensures both entities have complete address information when they represent the same person.

        Criteria for merging by similarity:
        - Names may repeat with additional surnames, merge them with the most complete name.
        - Identifiers are unique, if different names share an identifier, merge them using the most prominent name.

        For example, consider the following inputs and expected outputs:
        <creditors-input-example>
        [{"name": "Banco Consorcio", "identifier": "99.500.410-0"}, {"name": "Banco Consorc10", "identifier": "99.500.410-0"}, {"identifier": "99.500.410-0"}]
        </creditors-input-example>
        <creditors-output-example>
        [{"name": "Banco Consorcio", "identifier": "99.500.410-0"}]
        </creditors-output-example>
        <defendants-input-example>
        [
          {
            "name": "Felipe Corral",
            "identifier": "6.647.056-3",
            "address": "Av. Kennedy 7779 Departamento 42, Vitacura, Región Metropolitana",
            "legal_representatives": null
          },
          {
            "name": "VIA UNO CHILE SpA",
            "identifier": "76.055.749-8",
            "address": "Av. Del Parque 5275 Of. 203, Huechuraba, Región Metropolitana",
            "legal_representatives": [
              {
                "name": "Felipe Pizarro Corral",
                "identifier": null,
                "occupation": null,
                "address": null
              }
            ]
          },
          {
            "name": "Vía Uno Chile",
            "identifier": "76.055.749-8",
            "address": "Av. Del Parque 5275 Of. 203, Huechuraba",
            "legal_representatives": null
          }
        ]
        </defendants-input-example>
        <defendants-output-example>
        [
          {
            "name": "Vía Uno Chile SpA",
            "identifier": "76.055.749-8",
            "occupation": null,
            "address": "Av. Del Parque 5275 Of. 203, Huechuraba, Región Metropolitana",
            "legal_representatives": [
              {
                "name": "Felipe Pizarro Corral",
                "identifier": "6.647.056-3",
                "occupation": null,
                "address": "Av. Kennedy 7779 Departamento 42, Vitacura, Región Metropolitana"
              }
            ],
            "type": "debtor"
          },
          {
            "name": "Felipe Pizarro Corral",
            "identifier": "6.647.056-3",
            "address": "Av. Kennedy 7779 Departamento 42, Vitacura, Región Metropolitana",
            "legal_representatives": null,
            "type": "co_debtor"
          }
        ]
        </defendants-output-example>
        
        <address-complementation-example>
        If you have a co_debtor with identifier "6.647.056-3" and address "Av. Kennedy 7779 Departamento 42, Vitacura, Región Metropolitana",
        and a legal_representative with the same identifier "6.647.056-3" but missing address,
        then complement the legal_representative's address with the co_debtor's address.
        The same applies in reverse: if the legal_representative has the address but the co_debtor doesn't,
        complement the co_debtor's address with the legal_representative's address.
        </address-complementation-example>
        """

        prompt += f"""
        Now consider the real values:
        <creditors>{[creditor.model_dump_json() for creditor in information.creditors or []]}</creditors>
        <defendants>{[defendant.model_dump_json() for defendant in information.defendants or []]}</defendants>
        <sponsoring_attorneys>{[sponsoring_attorney.model_dump_json() for sponsoring_attorney in information.sponsoring_attorneys or []]}</sponsoring_attorneys>

        Return only unique items for each role list, when answering:
        - Use titlecase for names and addresses, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - Do not use fake or example data, only real data provided inside role tags.
        """
        result: DemandTextUniqueLitigants = self.merger.invoke(prompt)
        if result:
            information.creditors = result.creditors or information.creditors
            information.defendants = result.defendants or information.defendants
            information.sponsoring_attorneys = result.sponsoring_attorneys or information.sponsoring_attorneys
