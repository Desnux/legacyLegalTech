import logging

from examples.example_provider import ExampleProvider
from models.pydantic import (
    Bill,
    Creditor,
    FilledTemplate,
    Locale,
    MissingPaymentArgument,
    MissingPaymentArgumentReason,
    MissingPaymentDocumentType,
    PromissoryNote,
    SimulationInput,
)
from services.extractor import PromissoryNoteExtractor
from services.generator.base_generator import BaseGenerator


class MissingPaymentArgumentGenerator(BaseGenerator):
    def __init__(self, reason: MissingPaymentArgumentReason, seed: int = 0, locale: Locale = Locale.ES_ES) -> None:
        self.generator_template_llm = self.get_structured_template_filler(FilledTemplate)
        self.generator_llm = self.get_structured_generator(MissingPaymentArgument)
        self.generator_promissory_note_llm = self.get_structured_generator(PromissoryNote)
        self.generator_reason_llm = self.get_structured_generator(MissingPaymentArgumentReason)
        self.locale = locale
        self.reason = reason
        self.seed = seed
    
    def generate_from_file_path(self, file_path: str, document_type: MissingPaymentDocumentType) -> MissingPaymentArgument | None:
        if document_type == MissingPaymentDocumentType.PROMISSORY_NOTE:
            extractor = PromissoryNoteExtractor()
            promissory_note = extractor.extract_from_file_path(file_path)
            if promissory_note is None:
                logging.warning("Failed to extract promissory note")
                return None
            return self.generate_from_promissory_note(promissory_note)
        return None
    
    def generate_from_bill(self, bill: Bill, over_creditor: Creditor | None = None) -> MissingPaymentArgument | None:
        example_segments = self._get_example_segments(MissingPaymentDocumentType.BILL)
        if len(example_segments) == 0:
            argument: MissingPaymentArgument = self.generator_llm.invoke(self._get_bill_prompt(bill, over_creditor))
            argument.document_type = MissingPaymentDocumentType.BILL
            return argument
        
        segments: list[str] = []
        for idx, example_segment in enumerate(example_segments):
            if self.locale == Locale.ES_ES and not self.has_placeholder(example_segment):
                segments.append(example_segment)
            else:
                filled_template: FilledTemplate = self.generator_template_llm.invoke(self._get_bill_prompt(bill, over_creditor, example_segment, idx))
                if filled_template.result:
                    segments.append(filled_template.result.strip())

        argument = MissingPaymentArgument(argument="\n\n".join(segments))
        argument.document_type = MissingPaymentDocumentType.BILL
        return argument

    def generate_from_promissory_note(self, promissory_note: PromissoryNote) -> MissingPaymentArgument | None:
        example_segments = self._get_example_segments(MissingPaymentDocumentType.PROMISSORY_NOTE)
        if len(example_segments) == 0:
            argument: MissingPaymentArgument = self.generator_llm.invoke(self._get_promissory_note_prompt(promissory_note))
            argument.document_type = MissingPaymentDocumentType.PROMISSORY_NOTE
            return argument

        segments: list[str] = []
        for idx, example_segment in enumerate(example_segments):
            if self.locale == Locale.ES_ES and not self.has_placeholder(example_segment):
                segments.append(example_segment)
            else:
                filled_template: FilledTemplate = self.generator_template_llm.invoke(self._get_promissory_note_prompt(promissory_note, example_segment, idx))
                if filled_template.result:
                    segments.append(filled_template.result.strip())

        argument = MissingPaymentArgument(argument="\n\n".join(segments))
        argument.document_type = MissingPaymentDocumentType.PROMISSORY_NOTE
        return argument
    
    def generate_from_simulation(self, input: SimulationInput, document_type: MissingPaymentDocumentType = MissingPaymentDocumentType.PROMISSORY_NOTE) -> MissingPaymentArgument | None:
        if document_type == MissingPaymentDocumentType.PROMISSORY_NOTE:
            promissory_note = PromissoryNote.simulate(input, self.seed)
            if promissory_note is None:
                logging.warning("Failed to simulate promissory note")
                return None
            if len(self.reason.reason or "") == 0:
                self.reason = self.generator_reason_llm.invoke(promissory_note.get_prompt_reason())
            return self.generate_from_promissory_note(promissory_note)
        return None

    def _get_example_segments(self, document_type: MissingPaymentDocumentType) -> list[str]:
        try:
            example_documents = ExampleProvider().get_missing_payment_argument(document_type, self.seed)
        except Exception as e:
            example_documents = []
            logging.warning(f"Failed to get example documents: {e}")
        return [document.page_content for document in example_documents]

    def _get_bill_prompt(self, bill: Bill, over_creditor: Creditor | None, example: str = "", idx: int = -1) -> str:
        input = bill.model_dump()
        if over_creditor:
            input["over_creditor"] = {"name": over_creditor.name}
        input["creditors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, bill.creditors or []))
        input["debtors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, bill.debtors or []))

        short_input = {}
        if idx == 0:
            short_input = {
                "identifier": bill.identifier,
                "creditors": input["creditors"],
                "creation_date": bill.creation_date,
                "amount": bill.amount,
                "amount_currency": bill.amount_currency,
            }
            if over_creditor:
                short_input["over_creditor"] = {"name": over_creditor.name}
        elif idx == 2:
            short_input = {
                "debtors": list(map(lambda x: {"name": x.name}, bill.debtors or []))
            }
        elif idx == 3:
            short_input = {
                "reason": self.reason.reason,
                "pending_amount": self.reason.pending_amount if self.reason.pending_amount else bill.amount,
            }
            
        prompt = f"Consider the following bill attributes: <attributes>{input if idx == -1 else short_input}</attributes>"
        if len(example) > 0:
            prompt += f"""
            Your task is to generate a response given the attributes, following this template: <template>{example}</template>
            When answering:
            - Generate your response in {self.locale}.
            - Attributes match placeholders regardless of differences in plurality.
            - You must adjust either the inserted attributes and/or the text around them to ensure the result reads naturally, for example when dealing with plural or singular entities, or free form text attributes.
            - Do not use fake or example data, use only real data provided by the attributes.
            - If you are missing an attribute for a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
            - The result should be None or null if you cannot replace any placeholder, or the result would not provide valuable information without the values you are missing.
            """
            if idx == 0:
                prompt += "\n- If amount_currency is not CLP, you must indicate the currency type after the amount, for example in the case of USD: $1.000.000.- USD"
            if idx == 3:
                prompt += "\n- PAY ATTENTION, there is a {reason} placeholder in the template, when replacing it use consistent casing and adjust both it and the text around {reason} to be grammatically correct."
        else:
            prompt += f"\nGenerate a legal argument in {self.locale} to argue about missing payments."
        return prompt

    def _get_promissory_note_prompt(self, promissory_note: PromissoryNote, example: str = "", idx: int = -1) -> str:
        input = promissory_note.model_dump()
        input["creditors"] = list(map(lambda x: {"name": x.name}, promissory_note.creditors or []))
        input["debtors"] = list(map(lambda x: {"name": x.name}, promissory_note.debtors or []))
        input["co_debtors"] = list(map(lambda x: {"name": x.name}, promissory_note.co_debtors or []))

        short_input = {}
        if idx == 0:
            short_input = {
                "identifier": promissory_note.identifier,
                "creditors": input["creditors"],
                "creation_date": promissory_note.creation_date,
                "amount": promissory_note.amount,
                "amount_currency": promissory_note.amount_currency,
                "payment_installments": promissory_note.payment_installments,
                "payment_frequency": promissory_note.payment_frequency,
                "amount_per_installment": promissory_note.amount_per_installment,
                "amount_last_installment": promissory_note.amount_last_installment,
                "due_payment_day": promissory_note.due_payment_day,
                "first_installment_date": promissory_note.first_installment_date,
                "last_installment_date": promissory_note.last_installment_date,
            }
        elif idx == 1:
            short_input = {
                "interest_rate": promissory_note.interest_rate,
                "interest_rate_frequency": promissory_note.interest_rate_frequency,
                "interest_rate_base_days": promissory_note.interest_rate_base_days,
            }
        elif idx == 4:
            short_input = {
                "co_debtors": input["co_debtors"],
            }
        elif idx == 5:
            short_input = {
                "creditors": input["creditors"],
            }
        elif idx == 6:
            short_input = self.reason.model_dump()
        
        prompt = f"Consider the following promissory note attributes: <attributes>{input if idx == -1 else short_input}</attributes>"
        if len(example) > 0:
            prompt += f"""
            Your task is to generate a response given the attributes, following this template: <template>{example}</template>
            When answering:
            - Generate your response in {self.locale}.
            - Attributes match placeholders regardless of differences in plurality.
            - You must adjust either the inserted attributes and/or the text around them to ensure the result reads naturally, for example when dealing with plural or singular entities, or free form text attributes.
            - Do not use fake or example data, use only real data provided by the attributes.
            - If you are missing an attribute for a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
            - The result should be None or null if you cannot replace any placeholder, or the result would not provide valuable information without the values you are missing.
            - Add appropriate honorifics to names of people other than attorneys, such as don or doña for es_ES, exclude them from names of groups, businesses or institutions.
            """
            if idx == 0:
                prompt += "\n- If amount_currency is not CLP, you must indicate the currency type after the amount, for example in the case of USD: $1.000.000.- USD"
            if idx == 6:
                prompt += "\n- PAY ATTENTION, there is a {reason} placeholder in the template, when replacing it use consistent casing and adjust both it and the text around {reason} to be grammatically correct."
                prompt += "\n- Omit text related to pending, capital, interest, and debt amounts if those values are not specified directly or through {reason}, remove and adjust text around so it reads properly."
        else:
            prompt += f"\nGenerate a legal argument in {self.locale} to argue about missing payments."
        return prompt