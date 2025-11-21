import logging
from datetime import date

from models.pydantic import (
    DemandText,
    DispatchResolutionStructure,
    JudicialCollectionDemandTextStructure,
    JudicialCollectionDispatchResolution,
    JudicialCollectionDispatchResolutionDate,
    JudicialCollectionDispatchResolutionInput,
    JudicialCollectionDispatchResolutionPartial,
    Locale,
)
from services.extractor import DemandTextExtractor
from .base_generator import BaseGenerator


METRICS_SOFT_LOWER_BOUND = 0.75
METRICS_HARD_LOWER_BOUND = 0.4


class DispatchResolutionGenerator(BaseGenerator):
    def __init__(self, input: JudicialCollectionDispatchResolutionInput, seed: int = 0, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(JudicialCollectionDispatchResolution)
        self.generator_llm_partial = self.get_structured_generator(JudicialCollectionDispatchResolutionPartial)
        self.generator_date_llm = self.get_structured_generator(JudicialCollectionDispatchResolutionDate)
        self.locale = locale
        self.seed = seed
        self.valid_demand_text = True

    def generate_from_text(self, text: str) -> JudicialCollectionDispatchResolution | None:
        segments: list[str] = []

        extractor = DemandTextExtractor()
        demand_text = extractor.extract_from_text(text)
        if demand_text is None:
            logging.warning("Failed to extract demand text")
            return None

        header = self._generate_header()
        human_readable_issue_date = self._generate_human_readable_date(self.input.issue_date)
        resolution = self._generate_resolution(demand_text)
        requirements = self._generate_requirements()

        if header:
            segments.append(header)
        date_line = self._generate_date_line(human_readable_issue_date)
        if date_line:
            segments.append(date_line)
        if resolution:
            segments.append(resolution)
        if requirements and self.valid_demand_text:
            segments.append(requirements)
        footer = self._generate_footer(human_readable_issue_date)
        if footer:
            segments.append(footer)

        if len(segments) == 0:
            return None
        return JudicialCollectionDispatchResolution(text="\n\n".join(segments))

    def simulate_from_structured(self, structure: JudicialCollectionDemandTextStructure) -> DispatchResolutionStructure:
        header = self._generate_header()
        human_readable_issue_date = self._generate_human_readable_date(self.input.issue_date)
        date_line = self._generate_date_line(human_readable_issue_date)
        resolution: JudicialCollectionDispatchResolution = self.generator_llm.invoke(self._get_prompt_resolution(structure.additional_requests or ""))
        footer = self._generate_footer(human_readable_issue_date)
        return DispatchResolutionStructure(
            header=header,
            city=self.input.court_city,
            date_line=date_line,
            readable_date=human_readable_issue_date,
            resolution=resolution.text,
            footer=footer,
        )
    
    def _generate_date_line(self, readable_date: str | None) -> str | None:
        if readable_date and self.input.court_city:
            return f"{self.input.court_city.capitalize()}, {readable_date.lower()}."
        elif readable_date:
            return f"{readable_date.lower()}."
        elif self.input.court_city:
            return f"{self.input.court_city.capitalize()}."
        return None

    def _generate_header(self) -> str | None:
        if self.locale == Locale.EN_US:
            text = "NOMENCLATURE : 1. [67]Orders to dispatch writ"
        else:
            text = "NOMENCLATURA : 1. [67]Ordena despachar mandamiento"
        if self.input.court_number and self.input.court_city:
            if self.locale == Locale.EN_US:
                text += f"\nCOURT : {self.input.court_number}º Juzgado Civil de {self.input.court_city}"
            else:
                text += f"\nJUZGADO : {self.input.court_number}º Juzgado Civil de {self.input.court_city}"
        elif self.input.court_city:
            if self.locale == Locale.EN_US:
                text += f"\nCOURT : Juzgado Civil de {self.input.court_city}"
            else:
                text += f"\nJUZGADO : Juzgado Civil de {self.input.court_city}"
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
        return text
    
    def _generate_human_readable_date(self, query_date: date | None) -> str | None:
        if query_date is None:
            return None
        prompt = f"Given the following date: <date>{query_date}</date>"
        prompt += f"\nRewrite it with words in {self.locale} (format_example: dieciocho de febrero de dos mil veintiuno)"
        date_object: JudicialCollectionDispatchResolutionDate | None = None
        try:
            date_object = self.generator_date_llm.invoke(prompt)
        except Exception as e:
            logging.warning(f"Could not generate human readable date: {e}")
            date_object = None
        if date_object:
            return date_object.human_readable_date
        return query_date.strftime('%Y-%m-%d')

    def _generate_footer(self, readable_date: str | None) -> str | None:
        footer = ""
        if readable_date and self.input.court_city:
            footer = f"{self.input.court_city.capitalize()}, {readable_date.lower()}, "
        elif readable_date:
            footer = f"{readable_date.lower()}, "
        elif self.input.court_city:
            footer =  f"{self.input.court_city.capitalize()}, "
        
        if len(footer) > 0:
            if self.locale == Locale.EN_US:
                footer += "the preceding resolution was notified by the daily status."
            else:
                footer += "se notificó por el estado diario, la resolución precedente."
        else:
            if self.locale == Locale.EN_US:
                footer = "The preceding resolution was notified by the daily status."
            else:
                footer = "Se notificó por el estado diario, la resolución precedente."
        return footer if len(footer) > 0 else None

    def _generate_resolution(self, demand_text: DemandText) -> str | None:
        errors: list[str] = []
        if metrics := demand_text.metrics:
            if completeness := metrics.completeness:
                missing_elements: list[str] = []
                if len(demand_text.defendants or []) == 0:
                    missing_elements.append("Lacks information about defendants")
                if len(demand_text.plaintiffs or []) == 0:
                    missing_elements.append("Lacks information about plaintiffs")
                if len(demand_text.sponsoring_attorneys or []) == 0:
                    missing_elements.append("Lacks information about sponsoring_attorneys")
                if len(demand_text.requests or []) == 0:
                    missing_elements.append("Lacks legal requests this court could answer to")
                if completeness < METRICS_HARD_LOWER_BOUND:
                    errors.append("The demand text is barely more than a paragraph or sentence, it should not have been sent to the court, very unprofessional")
                if completeness < METRICS_SOFT_LOWER_BOUND:
                    if len(missing_elements > 0):
                        errors.append(f"The demand text lacks the following information to start the case: {missing_elements}")
                    else:
                        errors.append("The demand text lacks necessary information to start the case")
            if readability := metrics.readability:
                if readability < METRICS_SOFT_LOWER_BOUND and completeness > METRICS_HARD_LOWER_BOUND:
                    errors.append("The demand text is difficult to parse or is poorly written")
            if formality := metrics.formality:
                if formality < METRICS_SOFT_LOWER_BOUND and completeness > METRICS_HARD_LOWER_BOUND:
                    errors.append("The demand text contains informal language or is otherwise disrespectful")

        resolution: JudicialCollectionDispatchResolution | None = None
        if len(errors) > 0:
            self.valid_demand_text = False
            resolution = self.generator_llm.invoke(self._get_prompt_errors(errors))
        else:
            resolution = self.generator_llm.invoke(self._get_prompt_resolution(demand_text.requests or []))
        if resolution is None:
            return None
        return resolution.text

    def _generate_requirements(self) -> str | None:
        segments: list[str] = []
        for requirement in (self.input.requirements or []):
            if requirement.nature:
                prompt = requirement.nature.get_prompt(requirement.context or "", {}, self.locale)
                try:
                    request: JudicialCollectionDispatchResolution = self.generator_llm.invoke(prompt)
                except Exception as e:
                    logging.warning(f"Could not generate requirement: {e}")
                    continue
                segments.append(request.text)
        if len(segments) == 0:
            return None
        return "\n".join(segments)

    def _get_prompt_errors(self, errors: list[str]) -> str:
        prompt = f"Generate a formal legal resolution in {self.locale} that conveys the answer to a legal request using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure."
        prompt += f"\nIn this case, deny a request to start a case related to a judicial collection, given the following errors: <errors>{errors}</error>"
        prompt += "\nConsider this example of the expected vocabulary, do not copy information from the example: <example>En cuanto al curso progresivo solicitado, no habiéndose cumplido lo ordenado, no ha lugar.</example>"
        return prompt

    def _get_prompt_requirements(self) -> str:
        prompt = f"Generate a formal legal resolution in {self.locale} that conveys the answer to a legal request using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure."
        return prompt
    
    def _get_prompt_resolution(self, requests: list[str] | str) -> str:
        prompt = f"Generate a formal legal resolution in {self.locale} that conveys the answer to a legal request using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure."
        if len(requests) == 0:
            prompt += f"In this case, deny the request to start a case related to a judicial collection, given the lack of legal requests in the demand text."
            prompt += "Consider this example of the expected vocabulary, do not copy information from the example: <example>En cuanto al curso progresivo solicitado, no habiéndose cumplido lo ordenado, no ha lugar.</example>"
            return prompt
        prompt += f"\nIn this case, positively dispatch the request to start a case related to a judicial collection, and answer every secondary request: <requests>{requests}</requests>"
        prompt += "\nConsider this example of the expected vocabulary, do not copy information from the example: <example>A LO PRINCIPAL: Despéchese. AL PRIMERO Y SEGUNDO OTROSIES: Téngase presente con respecto a los bienes muebles señalados, designándose depositario provisional al propio ejecutado. AL TERCERO Y CUARTO OTROSIES: Téngase por acompañado los documentos, AL QUINTO OTROSI: Téngase presente.</example>"
        prompt += "\nIn general, dispatch the main resolution, acknowledge indications and designations (with a brief mention of what was indicated or designated), and give for accompanied any document or email from a request related to giving or sharing elements with the court."
        return prompt