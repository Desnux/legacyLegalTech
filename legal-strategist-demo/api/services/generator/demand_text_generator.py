import logging
import os
import random
import shutil
import tempfile
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from examples.example_provider import ExampleProvider
from models.api import DemandTextGenerationResponse
from models.pydantic import (
    Creditor,
    CurrencyType,
    Debtor,
    Defendant,
    DefendantType,
    ExpandedFilledTemplate,
    JudicialCollectionDemandText,
    DemandTextCorrectionInformation,
    JudicialCollectionDemandTextExtractedInfo,
    JudicialCollectionDemandTextInput,
    JudicialCollectionDemandTextPartial,
    JudicialCollectionDemandTextStructure,
    JudicialCollectionLegalRequest,
    LegalSubject,
    LegalRepresentative,
    Locale,
    MissingPaymentArgument,
    MissingPaymentArgumentReason,
    MissingPaymentDocumentType,
    MissingPaymentFile,
    PJUDABDTE,
    PJUDDDO,
    PJUDDTE,
    PJUDLegalRepresentative,
    Plaintiff,
    PromissoryNote,
    SimulationInput,
)
from services.extractor import AddressExtractor, BillExtractor, MissingPaymentReasonExtractor, PromissoryNoteExtractor
from util import int_to_ordinal
from .base_generator import BaseGenerator
from .demand_text_header_generator import DemandTextHeaderGenerator
from .missing_payment_argument_generator import MissingPaymentArgumentGenerator


class JudicialCollectionDemandTextGenerator(BaseGenerator):
    def __init__(self, input: JudicialCollectionDemandTextInput, seed: int = 0, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_template_llm = self.get_structured_template_filler(ExpandedFilledTemplate)
        self.generator_llm = self.get_structured_generator(JudicialCollectionDemandText)
        self.generator_llm_partial = self.get_structured_generator(JudicialCollectionDemandTextPartial)
        self.generator_reason_llm = self.get_structured_generator(MissingPaymentArgumentReason)
        self.locale = locale
        self.seed = seed
        self.merged_extracted_info: JudicialCollectionDemandTextExtractedInfo | None = None
        self.extracted_info: list[JudicialCollectionDemandTextExtractedInfo] = []
        self.document_files: list[MissingPaymentFile] = []
        self.correction_info = DemandTextCorrectionInformation()
        self.input.normalize()
    
    def generate_from_files(self, document_files: list[MissingPaymentFile], structured: bool = False) -> DemandTextGenerationResponse | None:
        self.document_files = document_files
        if all(map(lambda x: x.document_type == MissingPaymentDocumentType.PROMISSORY_NOTE, self.document_files)):
            self.input.legal_subject = LegalSubject.PROMISSORY_NOTE_COLLECTION
        elif all(map(lambda x: x.document_type == MissingPaymentDocumentType.BILL, self.document_files)):
            self.input.legal_subject = LegalSubject.BILL_COLLECTION
        else:
            self.input.legal_subject = LegalSubject.GENERAL_COLLECTION
        structure = self._generate()
        if not structured:
            raw_text = structure.to_raw_text()
            if raw_text is None:
                return None
            return DemandTextGenerationResponse(raw_text=raw_text, structured_output=None, correction_form=None)
        return DemandTextGenerationResponse(raw_text=None, structured_output=structure, correction_form=self.correction_info.get_as_form())

    def generate_from_simulation(self, input: SimulationInput) -> JudicialCollectionDemandText | None:
        structure = self._generate(input)
        raw_text = structure.to_raw_text()
        if raw_text is None:
            return None
        return JudicialCollectionDemandText(text=raw_text)

    def _generate(self, simulation_input: SimulationInput | None = None) -> JudicialCollectionDemandTextStructure:
        if simulation_input:
            missing_payment_arguments = self._simulate_missing_payment_arguments(simulation_input)
        else:
            missing_payment_arguments = self._generate_missing_payment_arguments()

        self._merge_extracted_info()
        header = self._generate_header()
        summary = self._generate_summary()

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_opening = executor.submit(self._generate_opening)
            future_main_request = executor.submit(self._generate_main_request)
            future_additional_requests = executor.submit(self._generate_additional_requests)
            opening = future_opening.result()
            main_request = future_main_request.result()
            additional_requests = future_additional_requests.result()

        sponsoring_attorneys = [
            PJUDABDTE(raw_name=attorney.name or "", identifier=attorney.identifier or "")
            for attorney in (self.input.sponsoring_attorneys or []) if attorney.identifier
        ]
        plaintiffs: list[PJUDDTE] = []
        for plaintiff in self.merged_extracted_info.creditors or []:
            pjud_dte = PJUDDTE(
                raw_address="",
                raw_name=plaintiff.name or "",
                identifier=plaintiff.identifier or "", 
                legal_representatives=[
                    PJUDLegalRepresentative(raw_name=representative.name or "", identifier=representative.identifier or "")
                    for representative in self.input.legal_representatives or []
                ],
            )
            plaintiffs.append(pjud_dte)
        
        address_extractor = AddressExtractor()
        defendants: list[PJUDDDO] = []
        for defendant in self.merged_extracted_info.defendants or []:
            pjud_ddo = PJUDDDO(
                raw_address=defendant.address or "",
                raw_name=defendant.name or "",
                identifier=defendant.identifier or "",
                legal_representatives=[
                    PJUDLegalRepresentative(raw_name=representative.name or "", identifier=representative.identifier or "")
                    for representative in defendant.legal_representatives or []
                ],
                addresses=[address_extractor.extract_from_text(defendant.address)] if defendant.address else [],
            )
            defendants.append(pjud_ddo)

        return JudicialCollectionDemandTextStructure(
            header=header,
            summary=summary,
            court=f"S.J.L CIVIL DE {self.merged_extracted_info.city.upper()}" if self.merged_extracted_info.city else None,
            opening=opening,
            missing_payment_arguments=missing_payment_arguments,
            main_request=main_request,
            additional_requests=additional_requests,
            sponsoring_attorneys=sponsoring_attorneys,
            plaintiffs=plaintiffs,
            defendants=defendants,
            legal_subject=self.input.legal_subject,
            city=self.merged_extracted_info.city,
        )

    def _generate_header(self) -> str:
        demand_text_header_generator = DemandTextHeaderGenerator(self.input.legal_subject)
        sponsoring_attorneys = self.input.sponsoring_attorneys or []
        if self.merged_extracted_info:
            plaintiffs = self.merged_extracted_info.creditors or []
            defendants = self.merged_extracted_info.defendants or []
        else:
            plaintiffs = []
            defendants = []
        return demand_text_header_generator.generate_from_litigants(plaintiffs, sponsoring_attorneys, defendants)
    
    def _generate_summary(self) -> str | None:
        segments: list[str] = []
        secondary_segments: list[str] = []
        affix: str = "ADDITIONAL"
        if self.locale == Locale.ES_ES:
            affix = "OTROSÍ"
        if self.input.main_request:
            if self.locale == Locale.ES_ES:
                segments.append("EN LO PRINCIPAL: DEMANDA EJECUTIVA Y SOLICITA SE DESPACHE MANDAMIENTO DE EJECUCIÓN Y EMBARGO")
            else:
                segments.append("MAINLY: EXECUTIVE DEMAND AND REQUEST FOR AN EXECUTION AND SEIZURE ORDER BE ISSUED")
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                if secondary_request.nature == JudicialCollectionLegalRequest.OTHER and secondary_request.context:
                    prompt = f"Generate a brief and formal legal sentence in {self.locale} that summarizes a request or obligation using an impersonal tone in less than 8 words."
                    prompt += f"\nFor context of the request or obligation, consider: <context>{secondary_request.context}</context>"
                    try:
                        request: JudicialCollectionDemandText = self.generator_llm.invoke(prompt)
                    except Exception as e:
                        logging.warning(f"Could not generate additional request summary: {e}")
                        continue
                    if request and request.text:
                        secondary_segments.append(request.text.upper())
                else:
                    secondary_segments.append(secondary_request.nature.to_localized_string(self.locale))
        if len(secondary_segments) > 0:
            numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(secondary_segments)]
            segments.extend(numbered_segments)
        if len(segments) == 0:
            return None
        return "; ".join(segments)

    def _generate_opening(self) -> str | None:
        opening: JudicialCollectionDemandText | None = None
        partial = JudicialCollectionDemandTextPartial(partial_text="")
        example_segments = self._get_example_segments("opening")
        if len(example_segments) == 0:
            opening = self.generator_llm.invoke(self._get_prompt_opening())
            if opening:
                return opening.text
            return None
        
        for idx, example_segment in enumerate(example_segments):
            last_partial = partial.partial_text[-self.get_last_partial_length():]
            partial_text: JudicialCollectionDemandTextPartial = self.generator_llm_partial.invoke(self._get_prompt_opening(last_partial, example_segment, idx, idx + 1 == len(example_segments)))
            partial = JudicialCollectionDemandTextPartial(partial_text=partial.partial_text.strip() + "\n\n" + partial_text.partial_text.strip())
        
        opening = JudicialCollectionDemandText(text=partial.partial_text)
        return opening.text

    def _generate_missing_payment_arguments(self) -> list[MissingPaymentArgument] | None:
        document_arguments: list[MissingPaymentArgument] = []
        reason_extractor = MissingPaymentReasonExtractor()

        def process_document(document_file: MissingPaymentFile, reason: str, index: int) -> tuple[int, MissingPaymentArgument | None, PromissoryNote | None]:
            if not document_file.document_type in [MissingPaymentDocumentType.BILL, MissingPaymentDocumentType.PROMISSORY_NOTE]:
                return index, None, None
            if document_file.upload_file is None:
                return index, None, None
            
            try:
                structured_reason = reason_extractor.extract_from_text(reason)
                if structured_reason is None:
                    raise ValueError("Null reason")
            except Exception as e:
                logging.warning(f"Could not extract missing payment reason: {e}")
                structured_reason = MissingPaymentArgumentReason(reason=reason)
            
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    shutil.copyfileobj(document_file.upload_file.file, temp_file)
                    temp_file_path = temp_file.name

                    bill = None
                    promissory_note = None
                    if document_file.document_type == MissingPaymentDocumentType.PROMISSORY_NOTE:
                        extractor = PromissoryNoteExtractor()
                        promissory_note = extractor.extract_from_file_path(temp_file_path)
                        if promissory_note is None:
                            logging.warning("Failed to extract attributes from promissory note")
                            return index, None, None, None
                        
                        defendants: list[Defendant] = []
                        for debtor in promissory_note.debtors or []:
                            defendants.append(Defendant(
                                name=debtor.name,
                                identifier=debtor.identifier,
                                occupation=None,
                                address=debtor.address,
                                legal_representatives=debtor.legal_representatives,
                                type=DefendantType.DEBTOR,
                            ))
                        for debtor in promissory_note.co_debtors or []:
                            defendants.append(Defendant(
                                name=debtor.name,
                                identifier=debtor.identifier,
                                occupation=None,
                                address=debtor.address,
                                legal_representatives=debtor.legal_representatives,
                                type=DefendantType.CO_DEBTOR,
                            ))
                        document_info = JudicialCollectionDemandTextExtractedInfo(
                            creditors=promissory_note.creditors,
                            debtors=promissory_note.debtors,
                            defendants=defendants,
                            co_debtors=promissory_note.co_debtors,
                            city=promissory_note.city,
                            amount=structured_reason.pending_amount or promissory_note.amount,
                            amount_currency=promissory_note.amount_currency,
                        )
                        self.extracted_info.append(document_info)

                        generator = MissingPaymentArgumentGenerator(structured_reason, self.seed, self.locale)
                        argument = generator.generate_from_promissory_note(promissory_note)
                    elif document_file.document_type == MissingPaymentDocumentType.BILL:
                        extractor = BillExtractor()
                        bill = extractor.extract_from_file_path(temp_file_path)
                        if bill is None:
                            logging.warning("Failed to extract attributes from bill")
                            return index, None, None, None
                        
                        defendants: list[Defendant] = []
                        for debtor in bill.debtors or []:
                            defendants.append(Defendant(
                                name=debtor.name,
                                identifier=debtor.identifier,
                                occupation=None,
                                address=debtor.address,
                                legal_representatives=debtor.legal_representatives,
                                type=DefendantType.DEBTOR,
                            ))
                        over_creditor: Creditor | None = None
                        if len(self.input.plaintiffs or []) > 0:
                            over_creditors = self.input.plaintiffs
                            over_creditor = Creditor(name=over_creditors[0].name, identifier=over_creditors[0].identifier)
                        document_info = JudicialCollectionDemandTextExtractedInfo(
                            creditors=[over_creditor] if over_creditor else bill.creditors,
                            debtors=bill.debtors,
                            defendants=defendants,
                            co_debtors=None,
                            city=bill.city,
                            amount=structured_reason.pending_amount or bill.amount,
                            amount_currency=bill.amount_currency,
                        )
                        self.extracted_info.append(document_info)
                        generator = MissingPaymentArgumentGenerator(structured_reason, self.seed, self.locale)
                        argument = generator.generate_from_bill(bill, over_creditor)

                    if argument is None:
                        logging.warning("Failed to generate missing payment argument")
                        return index, None, promissory_note, bill
                    return index, argument, promissory_note, bill
            except Exception as e:
                logging.warning(f"Error processing document ({type(e).__name__}): {e}")
                return index, None, None, None
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_document, document_file, reason, idx)
                for idx, (document_file, reason) in enumerate(zip(self.document_files, self.input.reasons_per_document or []))
            ]
            results = []
            for future in as_completed(futures):
                index, result, promissory_note, bill = future.result()
                if result:
                    results.append((index, result, promissory_note, bill))

        results.sort(key=lambda x: x[0])
        document_arguments = [result for _, result, _, _ in results]
        promissory_notes = [promissory_note for _, _, promissory_note, _ in results]
        bills = [bill for _, _, _, bill in results]
        
        if len(document_arguments) == 0:
            return None

        self.correction_info.bills = list(filter(None, bills))
        self.correction_info.promissory_notes = list(filter(None, promissory_notes))

        numbered_arguments = [
            MissingPaymentArgument(argument=f"{i + 1}) {segment.argument}", document_type=segment.document_type)
            for i, segment in enumerate(document_arguments)
        ]
        return numbered_arguments

    def _generate_main_request(self) -> str | None:
        main_request: JudicialCollectionDemandText | None = None
        partial = JudicialCollectionDemandTextPartial(partial_text="")
        example_segments = self._get_example_segments("main_request")
        if len(example_segments) == 0:
            main_request = self.generator_llm.invoke(self._get_prompt_main_request())
            if main_request:
                return main_request.text
            return None
        
        for idx, example_segment in enumerate(example_segments):
            last_partial = partial.partial_text[-self.get_last_partial_length():]
            partial_text: JudicialCollectionDemandTextPartial = self.generator_llm_partial.invoke(self._get_prompt_main_request(last_partial, example_segment, idx))
            partial = JudicialCollectionDemandTextPartial(partial_text=partial.partial_text.strip() + "\n\n" + partial_text.partial_text.strip())
        
        main_request = JudicialCollectionDemandText(text=partial.partial_text)
        return main_request.text

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        affix: str = "ADDITIONAL"
        if self.locale == Locale.ES_ES:
            affix = "OTROSÍ"
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                data = {}
                if secondary_request.nature == JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS:
                    data["documents"] = [{"document_type": df.document_type} for df in self.document_files]
                if secondary_request.nature == JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY:
                    data["plaintiffs"] = [{"name": creditor.name} for creditor in self.merged_extracted_info.creditors or []]
                if secondary_request.nature == JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER:
                    data["sponsoring_attorneys"] = [attorney.model_dump() for attorney in self.input.sponsoring_attorneys or []]
                prompt = secondary_request.nature.get_prompt((secondary_request.context or "").strip(), data, self.locale)
                try:
                    request: ExpandedFilledTemplate = self.generator_template_llm.invoke(prompt)
                    if request.result is None:
                        logging.warning(f"Could not generate additional request")
                except Exception as e:
                    logging.warning(f"Could not generate additional request: {e}")
                    continue
                segments.append(request.result)
        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)
    
    def _get_example_segments(self, section: str) -> list[str]:
        try:
            example_documents = ExampleProvider().get_judicial_collection_demand_text(section, self.seed)
        except Exception as e:
            example_documents = []
            logging.warning(f"Failed to get example documents: {e}")
        return [document.page_content for document in example_documents]
    
    def _get_prompt_main_request(self, partial: str = "", example: str = "", idx: int = -1) -> str:
        relevant_input = {
            "debtors": list(map(
                lambda x: {
                    "name": x.name, 
                    "legal_representatives": list(map(lambda x: {"name": x.name}, x.legal_representatives or [])),
                },
                self.merged_extracted_info.debtors or [])
            ),
            "co_debtors": list(map(lambda x: {"name": x.name}, self.merged_extracted_info.co_debtors or [])),
            "amount_in_dispute": self.merged_extracted_info.amount,
            "amount_currency": self.merged_extracted_info.amount_currency,
            "main_plaintiff_request": self.input.main_request or self.input.legal_subject,
        }
        if idx == 0:
            prompt = f"Consider the following segment for an example of the beginning of the closing section of a demand text: <example>{example}</example>"
            prompt += f"\nProduce the same segment in {self.locale}:"
            return prompt
        prompt = f"Consider the following information related to missing payment activities: <information>{relevant_input}</information>"
        if len(partial) > 0:
            prompt += f"\nContinue the closing section of a demand text in {self.locale} in order to start a judicial collection case related to missing payments."
            prompt += f"\nThis is the last segment of the ongoing closing section, start with the next character, without repeating information: <last_segment>{partial}</last_segment>"
        else:
            prompt += f"\nGenerate the closing section of a demand text in {self.locale} in order to start a judicial collection case related to missing payments."
        if len(example) > 0:
            prompt += f"\nConsider the following segment for an example of the legal structure that should follow up: <example>{example}</example>"
            prompt += f"\nIf there is information missing, ignore them in your argument, DO NOT copy information from the example."
            prompt += f"\nDo add appropriate honorifics to names of people, such as don or doña for es_ES, exclude them from names of groups, businesses or institutions."
        else:
            prompt += f"\nAllude to what has been exposed previously (will be prepended to your output), and any relevant legal article, then include the plaintiff request to the court in an organic manner."
            prompt += f"\nDo include the names of debtors and their legal representatives, alongside the amount in dispute."
        if idx == 1:
            prompt += "\nIf the main plaintiff request specifies an amount in dispute, consider it a more precise value that the one provided by other attributes."
        return prompt

    def _get_prompt_opening(self, partial: str = "", example: str = "", idx: int = -1, last: bool = False) -> str:
        relevant_input = {
            "creditor_sponsoring_attorneys": self.input.sponsoring_attorneys or [],
            "creditors": self.merged_extracted_info.creditors or [],
            "creditor_legal_representatives": self.input.legal_representatives or [],
            "debtors": self.merged_extracted_info.debtors or [],
            "co_debtors": self.merged_extracted_info.co_debtors or [],
        }
        if idx > 0:
            del relevant_input["creditor_legal_representatives"]
            del relevant_input["creditor_sponsoring_attorneys"]
        if idx > 1:
            del relevant_input["debtors"]
            del relevant_input["co_debtors"]
        prompt = f"Consider the following entitites involved in missing payment activities: <entities>{relevant_input}</entities>"
        if len(partial) > 0:
            prompt += f"\nContinue the opening section of a demand text in {self.locale} in order to start a judicial collection case related to missing payments."
            prompt += f"\nThis is the last segment of the ongoing opening section, start with the next character, without repeating information: <last_segment>{partial}</last_segment>"
        else:
            prompt += f"\nGenerate the opening section of a demand text in {self.locale} in order to start a judicial collection case related to missing payments."
        if len(example) > 0:
            prompt += f"\nConsider the following segment for an example of the legal structure that should follow up: <example>{example}</example>"
            prompt += f"\nIf there are entities missing, ignore them in your argument, DO NOT copy entities from the example."
            prompt += f"\nIf a specific value of an entity is missing, ignore it and adjust the text around it so the result reads naturally."
            prompt += f"\nDo add appropriate honorifics to names of people, such as don or doña for es_ES, exclude them from names of sponsoring attorneys, groups, businesses, or institutions."
            if last:
                prompt += f"\nEnd by declaring that your creditors names are owners and beneficiares of the following {'document [USE SINGULAR LANGUAGE]: (it' if len(self.extracted_info) < 0 else 'documents [USE PLURAL LANGUAGE]: (they'} will be appended to your output)"
        else:
            prompt += f"\nOverall, in the role of the sponsoring attorneys, introduce yourselves and the creditors you represent, mentioning their legal representatives attributes."
            prompt += f"\nFollow up by introducing the debtors and their legal representatives attributes, and finally, the co-debtors. Against whom you are redacting this executive demand."
            prompt += f"\nEnd by declaring that your creditors names are owners and beneficiares of the following {'document [USE SINGULAR LANGUAGE]: (it' if len(self.extracted_info) < 0 else 'documents [USE PLURAL LANGUAGE]: (they'} will be appended to your output)"
        return prompt
    
    def _merge_extracted_info(self) -> None:
        total_amount: int = 0
        total_amount_currency: CurrencyType = CurrencyType.CLP
        city: str | None = None
        unique_creditors: dict[str, Creditor] = {}
        unique_debtors: dict[str, Debtor] = {}
        unique_co_debtors: dict[str, Debtor] = {}
        unique_defendants: dict[str, Defendant] = {}

        for info in self.extracted_info:
            if info.amount:
                if info.amount_currency:
                    if info.amount_currency == total_amount_currency:
                        total_amount += info.amount
                    elif info.amount_currency == CurrencyType.USD:
                        total_amount += int(info.amount * 850.09)

            if info.city and city is None:
                city = info.city

            for creditor in info.creditors or []:
                if creditor.identifier is None:
                    continue
                key = creditor.identifier
                if key in unique_creditors:
                    unique_creditors[key] = self._merge_creditors(unique_creditors[key], creditor)
                else:
                    unique_creditors[key] = creditor

            for debtor in info.debtors or []:
                if debtor.identifier is None:
                    continue
                key = debtor.identifier
                if key in unique_debtors:
                    unique_debtors[key] = self._merge_debtors(unique_debtors[key], debtor)
                else:
                    unique_debtors[key] = debtor

            for co_debtor in info.co_debtors or []:
                if co_debtor.identifier is None:
                    continue
                key = co_debtor.identifier
                if key in unique_co_debtors:
                    unique_co_debtors[key] = self._merge_debtors(unique_co_debtors[key], co_debtor)
                else:
                    unique_co_debtors[key] = co_debtor
            
            for defendant in info.defendants or []:
                if defendant.identifier is None:
                    continue
                key = defendant.identifier
                if key in unique_defendants:
                    unique_defendants[key] = self._merge_defendants(unique_defendants[key], defendant)
                else:
                    unique_defendants[key] = defendant
        
        def merge_by_name(entities_dict: dict[str, Creditor | Debtor | Defendant], merge_func: Callable) -> dict[str, Creditor | Debtor | Defendant]:
            merged_entities = {}
            for entity in entities_dict.values():
                name_key = entity.name.lower()
                if name_key in merged_entities:
                    merged_entities[name_key] = merge_func(merged_entities[name_key], entity)
                else:
                    merged_entities[name_key] = entity
            return merged_entities
        
        unique_creditors = merge_by_name(unique_creditors, self._merge_creditors)
        unique_debtors = merge_by_name(unique_debtors, self._merge_debtors)
        unique_co_debtors = merge_by_name(unique_co_debtors, self._merge_debtors)
        unique_defendants = merge_by_name(unique_defendants, self._merge_defendants)
        unique_defendants = OrderedDict(
            sorted(unique_defendants.items(), key=lambda item: item[1].get_numeric_identifier(), reverse=True)
        )

        contained_creditors = self._get_contained_names([x.name for x in unique_creditors.values()])
        contained_debtors = self._get_contained_names([x.name for x in unique_debtors.values()])
        contained_co_debtors = self._get_contained_names([x.name for x in unique_co_debtors.values()])
        contained_defendants = self._get_contained_names([x.name for x in unique_defendants.values()])

        final_creditors = [u for u in list(unique_creditors.values()) if u.name not in contained_creditors]
        final_defendants = [u for u in list(unique_defendants.values()) if u.name not in contained_defendants]
        
        self.merged_extracted_info = JudicialCollectionDemandTextExtractedInfo(
            amount=total_amount,
            amount_currency=total_amount_currency,
            city=city,
            creditors=final_creditors,
            debtors=[u for u in list(unique_debtors.values()) if u.name not in contained_debtors],
            co_debtors=[u for u in list(unique_co_debtors.values()) if u.name not in contained_co_debtors],
            defendants=final_defendants,
        )
        self.correction_info.defendants = final_defendants
        self.correction_info.plaintiffs = [Plaintiff(**creditor.model_dump()) for creditor in final_creditors]
        self.correction_info.sponsoring_attorneys = self.input.sponsoring_attorneys

    def _merge_creditors(self, creditor_a: Creditor, creditor_b: Creditor) -> Creditor:
        if creditor_a.name and creditor_b.name:
            name = creditor_a.name if len(creditor_a.name) > len(creditor_b.name) else creditor_b.name
        else:
            name = creditor_a.name if creditor_a.name else creditor_b.name
        identifier = creditor_a.identifier if creditor_a.identifier else creditor_b.identifier
        return Creditor(name=name, identifier=identifier)

    def _merge_debtors(self, debtor_a: Debtor, debtor_b: Debtor) -> Debtor:
        if debtor_a.name and debtor_b.name:
            name = debtor_a.name if len(debtor_a.name) > len(debtor_b.name) else debtor_b.name
        else:
            name = debtor_a.name if debtor_a.name else debtor_b.name

        identifier = debtor_a.identifier if debtor_a.identifier else debtor_b.identifier

        if debtor_a.address and debtor_b.address:
            address = debtor_a.address if len(debtor_a.address) > len(debtor_b.address) else debtor_b.address
        else:
            address = debtor_a.address if debtor_a.address else debtor_b.address

        unique_legal_representatives: dict[str, LegalRepresentative] = {}
        for legal_representative in ((debtor_a.legal_representatives or []) + (debtor_b.legal_representatives or [])):
            if legal_representative.identifier is None:
                continue
            key = legal_representative.identifier
            if key in unique_legal_representatives:
                unique_legal_representatives[key] = self._merge_legal_representatives(unique_legal_representatives[key], legal_representative)
            else:
                unique_legal_representatives[key] = legal_representative
    
        return Debtor(name=name, identifier=identifier, address=address, legal_representatives=list(unique_legal_representatives.values()))

    def _merge_defendants(self, defendant_a: Defendant, defendant_b: Defendant) -> Defendant:
        if defendant_a.name and defendant_b.name:
            name = defendant_a.name if len(defendant_a.name) > len(defendant_b.name) else defendant_b.name
        else:
            name = defendant_a.name if defendant_a.name else defendant_b.name

        identifier = defendant_a.identifier if defendant_a.identifier else defendant_b.identifier

        if defendant_a.address and defendant_b.address:
            address = defendant_a.address if len(defendant_a.address) > len(defendant_b.address) else defendant_b.address
        else:
            address = defendant_a.address if defendant_a.address else defendant_b.address

        unique_legal_representatives: dict[str, LegalRepresentative] = {}
        for legal_representative in ((defendant_a.legal_representatives or []) + (defendant_b.legal_representatives or [])):
            if legal_representative.identifier is None:
                continue
            key = legal_representative.identifier
            if key in unique_legal_representatives:
                unique_legal_representatives[key] = self._merge_legal_representatives(unique_legal_representatives[key], legal_representative)
            else:
                unique_legal_representatives[key] = legal_representative

        if defendant_a.type and defendant_b.type:
            defendant_type = defendant_a.type if defendant_a.type == DefendantType.DEBTOR else defendant_b.type
        else:
            defendant_type = defendant_a.type if defendant_a.type else defendant_b.type

        return Defendant(
            name=name, 
            identifier=identifier,
            occupation=None,
            address=address,
            legal_representatives=list(unique_legal_representatives.values()),
            type=defendant_type,
        )

    def _merge_legal_representatives(self, legal_representative_a: LegalRepresentative, legal_representative_b: LegalRepresentative) -> LegalRepresentative:
        if legal_representative_a.name and legal_representative_b.name:
            name = legal_representative_a.name if len(legal_representative_a.name) > len(legal_representative_b.name) else legal_representative_b.name
        else:
            name = legal_representative_a.name if legal_representative_a.name else legal_representative_b.name

        identifier = legal_representative_a.identifier if legal_representative_a.identifier else legal_representative_b.identifier

        if legal_representative_a.address and legal_representative_b.address:
            address = legal_representative_a.address if len(legal_representative_a.address) > len(legal_representative_b.address) else legal_representative_b.address
        else:
            address = legal_representative_a.address if legal_representative_a.address else legal_representative_b.address

        if legal_representative_a.occupation and legal_representative_b.occupation:
            occupation = legal_representative_a.occupation if len(legal_representative_a.occupation) > len(legal_representative_b.occupation) else legal_representative_b.occupation
        else:
            occupation = legal_representative_a.occupation if legal_representative_a.occupation else legal_representative_b.occupation
        return LegalRepresentative(name=name, identifier=identifier, address=address, occupation=occupation)
    
    def _simulate_missing_payment_arguments(self, simulation_input: SimulationInput) -> list[MissingPaymentArgument] | None:
        local_random = random.Random(self.seed if self.seed != 0 else None)
        document_amount = local_random.randint(1, 4)
        document_arguments: list[MissingPaymentArgument] = []

        for idx in range(document_amount):
            sub_seed = self.seed + idx if self.seed != 0 else 0
            promissory_note = PromissoryNote.simulate(simulation_input, sub_seed)
            reason: MissingPaymentArgumentReason = self.generator_reason_llm.invoke(promissory_note.get_prompt_reason())
            defendants: list[Defendant] = []
            for debtor in promissory_note.debtors or []:
                defendants.append(Defendant(
                    name=debtor.name,
                    identifier=debtor.identifier,
                    occupation=None,
                    address=debtor.address,
                    legal_representatives=debtor.legal_representatives,
                    type=DefendantType.DEBTOR,
                ))
            for debtor in promissory_note.co_debtors or []:
                defendants.append(Defendant(
                    name=debtor.name,
                    identifier=debtor.identifier,
                    occupation=None,
                    address=debtor.address,
                    legal_representatives=debtor.legal_representatives,
                    type=DefendantType.CO_DEBTOR,
                ))
            document_info = JudicialCollectionDemandTextExtractedInfo(
                creditors=promissory_note.creditors,
                debtors=promissory_note.debtors,
                defendants=defendants,
                co_debtors=promissory_note.co_debtors,
                city=promissory_note.city,
                amount=promissory_note.amount,
                amount_currency=promissory_note.amount_currency,
            )
            self.extracted_info.append(document_info)

            try:
                generator = MissingPaymentArgumentGenerator(reason, sub_seed, self.locale)
                argument = generator.generate_from_promissory_note(promissory_note)
            except Exception as e:
                logging.warning(f"Failed to simulate missing payment argument: {e}")
                continue
            document_arguments.append(argument)

        if len(document_arguments) == 0:
            return None
        
        numbered_arguments = [
            MissingPaymentArgument(argument=f"{i + 1}) {segment.argument}", document_type=segment.document_type)
            for i, segment in enumerate(document_arguments)
        ]
        return numbered_arguments

    def _get_contained_names(self, names: list[str | None]) -> list[str]:
        names_sorted = sorted([name for name in names if name], key=lambda x: len(x), reverse=True)
        contained_names = []
        for name in names_sorted:
            current_components = set(name.lower().split())
            if any(current_components.issubset(set(existing.lower().split())) and current_components != set(existing.lower().split()) for existing in names_sorted):
                contained_names.append(name)
        return contained_names