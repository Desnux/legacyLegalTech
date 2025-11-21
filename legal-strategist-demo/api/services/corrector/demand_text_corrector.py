from collections import defaultdict

from pydantic import BaseModel, Field

from examples.example_provider import ExampleProvider
from models.pydantic import (
    CorrectionField,
    CorrectionFieldList,
    DemandTextCorrectionForm,
    JudicialCollectionDemandTextStructure,
    LegalSubject,
    Litigant,
    Locale,
    MissingPaymentArgument,
    MissingPaymentDocumentType,
    PJUDDDO,
    PJUDLegalRepresentative,
)
from services.extractor import AddressExtractor
from services.generator import DemandTextHeaderGenerator
from .base_corrector import BaseCorrector


class Response(BaseModel):
    new_segment: str = Field(..., description="Rewritten segment")


class DemandTextCorrector(BaseCorrector):
    def __init__(self, correction_form: DemandTextCorrectionForm, locale: Locale = Locale.ES_ES) -> None:
        self.correction_form = correction_form
        self.correction_llm = self.get_structured_corrector(Response)
        self.locale = locale
    
    def generate_from_structured_output(self, structured_output: JudicialCollectionDemandTextStructure) -> JudicialCollectionDemandTextStructure | None:
        demand_text_header_generator = DemandTextHeaderGenerator(structured_output.legal_subject or LegalSubject.GENERAL_COLLECTION)
        defendants: list[Litigant] = []
        plaintiffs: list[Litigant] = []
        pjud_defendants: list[PJUDDDO] = []
        sponsoring_attorneys: list[Litigant] = []

        for defendant_fields in self.correction_form.defendants:
            initial_address = self._get_initial_value(defendant_fields, "address")
            corrected_address = self._get_corrected_value(defendant_fields, "address")
            name = self._get_corrected_value(defendant_fields, "name")
            identifier = self._get_corrected_value(defendant_fields, "identifier")
            legal_representatives = [
                Litigant(
                    name=self._get_corrected_value(legal_representative_fields, "name"),
                    identifier=self._get_corrected_value(legal_representative_fields, "identifier"),
                )
                for legal_representative_fields in self._get_corrected_values(defendant_fields, "legal_representatives.")
            ]
            defendants.append(Litigant(
                name=self._get_corrected_value(defendant_fields, "name"),
                identifier=identifier,
                legal_representatives=legal_representatives,
            ))
            pjud_defendant = next(filter(lambda pjud_defendant: pjud_defendant.identifier == identifier, structured_output.defendants), None)
            addresses = pjud_defendant.addresses if pjud_defendant else []
            if corrected_address is None:
                addresses = []
            elif initial_address != corrected_address or len(addresses) == 0:
                address_extractor = AddressExtractor()
                addresses = [address_extractor.extract_from_text(corrected_address)]
            pjud_defendants.append(PJUDDDO(
                raw_address=corrected_address or "",
                raw_name=name or "",
                identifier=identifier or "",
                legal_representatives=[
                    PJUDLegalRepresentative(raw_name=legal_representative.name or "", identifier=legal_representative.identifier or "")
                    for legal_representative in legal_representatives
                ],
                addresses=addresses,
            ))
        
        for plaintiff_fields in self.correction_form.plaintiffs:
            plaintiffs.append(Litigant(
                name=self._get_corrected_value(plaintiff_fields, "name"),
                identifier=self._get_corrected_value(plaintiff_fields, "identifier"),
            ))

        for sponsoring_attorney_fields in self.correction_form.sponsoring_attorneys:
            sponsoring_attorneys.append(Litigant(
                name=self._get_corrected_value(sponsoring_attorney_fields, "name"),
                identifier=self._get_corrected_value(sponsoring_attorney_fields, "identifier"),
            ))

        structured_output.header = demand_text_header_generator.generate_from_litigants(plaintiffs, sponsoring_attorneys, defendants)
        structured_output.defendants = pjud_defendants
        
        if missing_payment_arguments := structured_output.missing_payment_arguments:
            example_provider = ExampleProvider()

            bill_example = "\n".join([i.page_content for i in example_provider.get_missing_payment_argument(MissingPaymentDocumentType.BILL)])
            bills_info = list(filter(lambda x: x.document_type == MissingPaymentDocumentType.BILL, missing_payment_arguments))

            promissory_note_example = "\n".join([i.page_content for i in example_provider.get_missing_payment_argument(MissingPaymentDocumentType.PROMISSORY_NOTE)])
            promissory_notes_info = list(filter(lambda x: x.document_type == MissingPaymentDocumentType.PROMISSORY_NOTE, missing_payment_arguments))

            type_positions = defaultdict(list)

            for index, missing_payment_argument in enumerate(missing_payment_arguments):
                type_positions[missing_payment_argument.document_type].append(index)

            for index, (previous, corrected_fields) in enumerate(zip(promissory_notes_info, self.correction_form.promissory_notes)):
                changed_fields = [field for field in corrected_fields if field.has_changed()]
                updated_fields = [field.get_change() for field in changed_fields]
                if changed_fields:
                    response: Response = self.correction_llm.invoke(self._get_missing_payment_argument_prompt(previous.argument, updated_fields, promissory_note_example))
                    structured_output.missing_payment_arguments[type_positions[ MissingPaymentDocumentType.PROMISSORY_NOTE][index]] = MissingPaymentArgument(
                        argument=response.new_segment,
                        document_type=MissingPaymentDocumentType.PROMISSORY_NOTE,
                    )
            
            for index, (previous, corrected_fields) in enumerate(zip(bills_info, self.correction_form.bills)):
                changed_fields = [field for field in corrected_fields if field.has_changed()]
                updated_fields = [field.get_change() for field in changed_fields]
                if changed_fields:
                    response: Response = self.correction_llm.invoke(self._get_missing_payment_argument_prompt(previous.argument, updated_fields, bill_example))
                    structured_output.missing_payment_arguments[type_positions[MissingPaymentDocumentType.BILL][index]] = MissingPaymentArgument(
                        argument=response.new_segment,
                        document_type=MissingPaymentDocumentType.BILL,
                   )
                
        return structured_output
    
    def _get_initial_value(self, fields: list[CorrectionField | CorrectionFieldList], name: str) -> str | None:
        return next(map(lambda field: field.initial_value, filter(lambda field: field.name == name, fields)), None)

    def _get_corrected_value(self, fields: list[CorrectionField | CorrectionFieldList], name: str) -> str | None:
        return next(map(lambda field: field.corrected_value, filter(lambda field: field.name == name, fields)), None)
    
    def _get_corrected_values(self, fields: list[CorrectionField | CorrectionFieldList], name: str) -> list[list[CorrectionField]]:
        return list(map(lambda field: field.corrected_value, filter(lambda field: field.name.startswith(name), fields)))
    
    def _get_missing_payment_argument_prompt(self, previous: str, updated_fields: dict, example: str | None) -> str:
        prompt = f"""
        Consider the following segment of a demand text:
        <segment>{previous}</segment>
        The following information fields have been updated, removed, or added:
        <fields>{updated_fields}</fields>
        Rewrite the segment in {self.locale} with the new values.
        When answering:
            - Return only the new segment.
            - Preserve the prefixed enumeration.
            - If the new value is null or None, remove it from the segment and adjust the text around as to preserve grammatic and logic.
        """
        if example:
            prompt += f"""- If the previous value was null or None, add the new value where it would be found in the example provided.
            - Preserve all other information as it is.
                
        <example>{example}</example>
            """
        else:
            prompt += """- If the previous value was null or None, add the new value where it makes the most sense and adjust the text around it.
            - Preserve all other information as it is.
            """
        return prompt
