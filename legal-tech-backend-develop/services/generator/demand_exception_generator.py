import logging

from pydantic import BaseModel, Field

from examples.example_provider import ExampleProvider
from models.pydantic import (
    DemandExceptionStructure,
    JudicialCollectionDemandException,
    JudicialCollectionDemandExceptionInput,
    JudicialCollectionDemandExceptionPartial,
    JudicialCollectionDemandExceptionRequest,
    JudicialCollectionDemandExceptionSecondaryRequest,
    LegalExceptionRequest,
    LegalException,
    Locale,
)
from services.extractor import DemandTextExtractor
from services.v2.document.demand_text import DemandTextStructure
from util import int_to_ordinal
from .base_generator import BaseGenerator


class ExceptionsAndRequests(BaseModel):
    exceptions: list[JudicialCollectionDemandExceptionRequest] | None = Field(None, description="Exceptions to raise alongside the necessary context to raise them")
    secondary_requests: list[JudicialCollectionDemandExceptionSecondaryRequest] | None = Field(None, description="Secondary requests directed to the court, alongside the necessary context")


class DemandExceptionGenerator(BaseGenerator):
    def __init__(self, input: JudicialCollectionDemandExceptionInput, seed: int = 0, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(JudicialCollectionDemandException)
        self.generator_llm_partial = self.get_structured_generator(JudicialCollectionDemandExceptionPartial)
        self.generator_exceptions_and_requests_llm = self.get_structured_generator(ExceptionsAndRequests)
        self.locale = locale
        self.seed = seed
        self.exceptions_context: dict[LegalException, str] = {}
    
    def generate_from_text(self, text: str) -> JudicialCollectionDemandException | None:
        segments: list[str] = []

        extractor = DemandTextExtractor()
        demand_text = extractor.extract_from_text(text)
        if demand_text is None:
            logging.warning("Failed to extract demand text")
        else:
            self.input.plaintiffs = self.input.plaintiffs or demand_text.plaintiffs
            self.input.defendants = self.input.defendants or demand_text.defendants
            exceptions_to_extract: list[LegalException] = []
            for exception in self.input.exceptions or []:
                if exception.nature and len(exception.context or "") == 0:
                    exceptions_to_extract.append(exception.nature)
            demand_text_for_exceptions = extractor.extract_for_exceptions_from_text(text, exceptions_to_extract)
            if len(exceptions_to_extract) > 0 and demand_text_for_exceptions is None:
                logging.warning("Failed to extract context for exceptions")
            else:
                self.exceptions_context = demand_text_for_exceptions

        header = self._generate_header()
        opening = self._generate_opening()
        summary = self._generate_summary()
        exceptions = self._generate_exceptions()
        main_request = self._generate_main_request()
        additional_requests = self._generate_additional_requests()
        
        if header:
            segments.append(header)
        if summary:
            segments.append(summary)
        segments.append("S.J.L.")
        if opening:
            segments.append(opening)
        if exceptions:
            segments.append(exceptions)
        if main_request:
            segments.append(main_request)
        if additional_requests:
            segments.append(additional_requests)
        if len(segments) == 0:
            return None
        return JudicialCollectionDemandException(text="\n\n".join(segments))

    def simulate_from_structured(self, structure: DemandTextStructure) -> DemandExceptionStructure:
        available_exceptions = list(LegalException)
        available_requests = list(LegalExceptionRequest)
        exceptions_and_requests: ExceptionsAndRequests = self.generator_exceptions_and_requests_llm.invoke(
            self._get_prompt_exceptions_and_requests(structure.to_raw_text(), available_exceptions, available_requests)
        )
        self.input.exceptions = exceptions_and_requests.exceptions
        self.input.secondary_requests = exceptions_and_requests.secondary_requests

        header = self._generate_header()
        opening = self._generate_opening()
        summary = self._generate_summary()
        exceptions = self._generate_exceptions()
        main_request = self._generate_main_request()
        additional_requests = self._generate_additional_requests()
        return DemandExceptionStructure(
            header=header,
            summary=summary,
            opening=opening,
            exceptions=exceptions,
            main_request=main_request,
            additional_requests=additional_requests,
        )

    def _generate_header(self) -> str | None:
        text: str = ""
        if self.input.court_number and self.input.court_city:
            if self.locale == Locale.EN_US:
                text += f"COURT : {self.input.court_number}º Juzgado Civil de {self.input.court_city}"
            else:
                text += f"JUZGADO : {self.input.court_number}º Juzgado Civil de {self.input.court_city}"
        elif self.input.court_city:
            if self.locale == Locale.EN_US:
                text += f"COURT : Juzgado Civil de {self.input.court_city}"
            else:
                text += f"JUZGADO : Juzgado Civil de {self.input.court_city}"
        if self.input.case_role:
            if self.locale == Locale.EN_US:
                text += f"\nCASE ROLE : {self.input.case_role}"
            else:
                text += f"\nCAUSA ROL : {self.input.case_role}"
        if self.input.case_title:
            if self.locale == Locale.EN_US:
                text += f"\nTITLE : {self.input.case_title}"
            else:
                text += f"\nCARATULADO : {self.input.case_title}"
        if len(text) == 0:
            return None
        return text

    def _generate_summary(self) -> str | None:
        segments: list[str] = []
        secondary_segments: list[str] = []
        affix: str = "ADDITIONAL"
        if self.locale == Locale.ES_ES:
            affix = "OTROSÍ"
        if self.locale == Locale.ES_ES:
            segments.append("EN LO PRINCIPAL: EXCEPCIONES")
        else:
            segments.append("MAINLY: EXCEPTIONS")
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                if secondary_request.nature == LegalExceptionRequest.OTHER and secondary_request.context:
                    prompt = f"Generate a brief and formal legal sentence in {self.locale} that summarizes a request or obligation using an impersonal tone in less than 8 words."
                    prompt += f"\nFor context of the request or obligation, consider: <context>{secondary_request.context}</context>"
                    try:
                        request: JudicialCollectionDemandException = self.generator_llm.invoke(prompt)
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
        opening: JudicialCollectionDemandException | None = None
        partial = JudicialCollectionDemandExceptionPartial(partial_text="")
        example_segments = self._get_example_segments("opening")
        if len(example_segments) == 0:
            opening = self.generator_llm.invoke(self._get_prompt_opening())
            if opening:
                return opening.text
            return None
        
        for idx, example_segment in enumerate(example_segments):
            last_partial = partial.partial_text[-self.get_last_partial_length():]
            partial_text: JudicialCollectionDemandExceptionPartial = self.generator_llm_partial.invoke(self._get_prompt_opening(last_partial, example_segment, idx, idx + 1 == len(example_segments)))
            partial = JudicialCollectionDemandExceptionPartial(partial_text=partial.partial_text.strip() + " " + partial_text.partial_text.strip())
        
        opening = JudicialCollectionDemandException(text=partial.partial_text)
        return opening.text

    def _generate_exceptions(self) -> str | None:
        segments: list[str] = []
        affix: str = "EXCEPTION"
        if self.locale == Locale.ES_ES:
            affix = "EXCEPCIÓN"
        for exception in self.input.exceptions or []:
            if nature := exception.nature:
                sub_segment = nature.to_localized_string(self.locale)

                data = {}
                if nature.plaintiffs_are_relevant():
                    data["plaintiffs"] = [plaintiff.model_dump(exclude={"identifier"}) for plaintiff in self.input.plaintiffs or []]
                if nature.demand_text_date_is_relevant():
                    data["plaintiff_filed_demand_text_date"] = self.input.demand_text_date
                data["defendants"] = []
                for defendant in self.input.defendants or []:
                    dumped = defendant.model_dump(exclude={"identifier", "legal_representatives"})

                    # 🔴 CORRECCIÓN CLAVE:
                    # Si es persona natural, dejar explícito que actúa por derecho propio
                    if defendant.entity_type == "natural":
                        dumped["representation"] = "actúa por derecho propio"
                    else:
                        # Persona jurídica → puede tener representante legal
                        dumped["representation"] = "representado legalmente"

                    data["defendants"].append(dumped)
                if nature.court_is_relevant():
                    data["court_city"] = self.input.court_city
                if nature.plaintiff_attorneys_are_relevant():
                    data["plaintiffs_attorneys"] = [plaintiff_attorney.model_dump(exclude={"identifier"}) for plaintiff_attorney in self.input.plaintiff_attorneys or []]
                context = exception.context or ""
                if len(context) == 0 and len(self.exceptions_context.get(nature, "")) > 0:
                    context = self.exceptions_context[nature]
                prompt = nature.get_prompt(context, data, self.locale)
                try:
                    request: JudicialCollectionDemandException | None = self.generator_llm.invoke(prompt)
                except Exception as e:
                    request = None
                    logging.warning(f"Could not generate specific exception: {e}")
                
                if request:
                    segments.append(request.text)
                else:
                    segments.append(sub_segment)

        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, self.locale, True)} {affix}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _generate_main_request(self) -> str | None:
        prompt = f"""
        Generate a formal legal statement in {self.locale} that conveys a request using an impersonal tone, formal legal vocabulary, and complex sentence structure.
        The language should reflect a high level of authority and precision, similar to how official legal documents are written.
        Consider the following template, localize it and modify it as you see fit:
        <template>
        POR TANTO, de acuerdo con las disposiciones referidas y lo establecido por los artículos 459 y siguientes y 465 y siguientes del Código de Procedimiento Civil,
        
        RUEGO A US. tener por opuestas las excepciones, acogerlas a tramitación, y en definitiva, rechazar la demanda ejecutiva en todas sus partes, con expresa condenación en costas.
        </template>"
        """
        main_request: JudicialCollectionDemandException = self.generator_llm.invoke(prompt)
        return main_request.text

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        affix: str = "ADDITIONAL"
        if self.locale == Locale.ES_ES:
            affix = "OTROSÍ"
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                data = {}
                if secondary_request.nature == LegalExceptionRequest.ACCREDIT_PERSONALITY:
                    data["defendants"] = list(map(lambda x: {"name": x.name}, self.input.defendants or []))
                if secondary_request.nature == LegalExceptionRequest.SPONSORSHIP_AND_POWER:
                    data["defendant_attorneys"] = self.input.defendant_attorneys or []
                prompt = secondary_request.nature.get_prompt(secondary_request.context or "", data, self.locale)
                try:
                    request: JudicialCollectionDemandException = self.generator_llm.invoke(prompt)
                except Exception as e:
                    logging.warning(f"Could not generate additional request: {e}")
                    continue
                segments.append(request.text)
        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _get_example_segments(self, section: str) -> list[str]:
        try:
            example_documents = ExampleProvider().get_judicial_collection_demand_exception(section, self.seed)
        except Exception as e:
            example_documents = []
            logging.warning(f"Failed to get example documents: {e}")
        return [document.page_content for document in example_documents]

    def _get_prompt_opening(self, partial: str = "", example: str = "", idx: int = -1, last: bool = False) -> str:
        relevant_input = {
            "case_role": self.input.case_role,
            "case_title": self.input.case_title,
            "demand_text_date": self.input.demand_text_date,
            "plaintiffs": self.input.plaintiffs or [],
            "defendants": self.input.defendants or [],
            "defendant_attorneys": self.input.defendant_attorneys or [],  
        }
        if idx == 0:
            del relevant_input["plaintiffs"]
            del relevant_input["demand_text_date"]
        if idx > 0:
            del relevant_input["case_role"]
            del relevant_input["case_title"]
        prompt = f"Consider the following attributes involved in a legal case related to missing payments: <attributes>{relevant_input}</attributes>"
        if len(partial) > 0:
            prompt += f"\nContinue the opening section of a text of exceptions in {self.locale} in order to stop a judicial collection case related to missing payments."
            prompt += f"\nThis is the last segment of the ongoing opening section, start with the next character, without repeating information: <last_segment>{partial}</last_segment>"
        else:
            prompt += f"\nGenerate the opening section of a text of exceptions in {self.locale} in order to stop a judicial collection case related to missing payments."
        if len(example) > 0:
            prompt += f"\nConsider the following segment for an example of the legal structure that should follow up: <example>{example}</example>"
            prompt += f"\nIf there are attributes missing, ignore them in your argument, DO NOT copy attributes from the example."
            prompt += f"\nDo add appropriate honorifics to names of people, such as don or doña for es_ES, exclude them from names of groups, businesses or institutions."
            if last:
                prompt += f"\nEnd by declaring that in the name of the defendants, you are going to raise the following exceptions: [end with ':', the exceptions will be appended to your output]"
        else:
            prompt += f"\nOverall, in the role of the defendant attorneys, introduce yourselves and the defendants you represent."
            prompt += f"\nFollow up by mentioning the case title and role, the date when the demand text was filed, and finally, the plaintiffs. Against whom you are redacting this text of exceptions."
            prompt += f"\nEnd by declaring that in the name of the defendants, you are going to raise the following exceptions: [end with ':', the exceptions will be appended to your output]"
        return prompt
    
    def _get_prompt_exceptions_and_requests(self, text: str, available_exceptions: list[LegalException], available_requests: list[LegalExceptionRequest]) -> str:
        prompt = f"""
        Consider the following demand text written by the plaintiffs: <demand>{text}</demand>
        In your role as the defendant attorney, determine the best exceptions and requests to raise, accompanied by valid and real context in {self.locale}.
        At minimum, you should raise the means_of_proof request, unless otherwise specified.
        """
        return prompt
