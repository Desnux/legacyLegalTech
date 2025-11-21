from datetime import datetime

from pydantic import BaseModel, Field

from models.pydantic import (
    DispatchResolutionStructure,
    JudicialCollectionDemandTextStructure,
    LegalResponse,
    LegalResponseInput,
    Locale,
)
from .base_generator import BaseGenerator


class Response(BaseModel):
    text: str | None = Field(None, description="Generation output")


class LegalResponseGenerator(BaseGenerator):
    def __init__(self, input: LegalResponseInput, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(Response)
        self.locale = locale
    
    def generate_from_dispatch_resolution(self, dispatch_resolution: DispatchResolutionStructure, demand_text: JudicialCollectionDemandTextStructure | None = None) -> LegalResponse:
        demand_text_content = demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"}) if demand_text else ""
        header = self._generate_header()
        court = self._generate_court()
        response = self._generate_dispatch_resolution_response(dispatch_resolution.to_raw_text(), demand_text_content, "resolution")
        request = self._generate_request()
        return LegalResponse(
            header=header,
            court=court,
            response=response,
            request=request,
        )

    def _generate_court(self) -> str:
        if self.input.court_city and self.input.court_number:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()} ({self.input.court_number}º)"
        if self.input.court_city:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()}"
        return "S.J.L."
    
    def _generate_header(self) -> str:
        return "CUMPLE CON LO ORDENADO"
    
    def _generate_dispatch_resolution_response(self, dispatch_resolution: str, demand_text: str) -> str:
        template = """
        {attorney.name}, abogado, por el ejecutante, en los autos caratulados “{case_title}”, ROL {case_role}, a US., con respeto digo:\n\n
        Que por este acto, vengo en dar cumplimiento a lo ordenado con fecha {resolution_date (format_example: 10 de febrero de 2021)}, {response_body}
        """
        prompt = f"""
        Generate a legal response in {self.locale} to the following resolution:
        <resolution>{dispatch_resolution}</resolution>

        In order to respond, consider the following template and adjust information where needed, you also have to generate the response_body section:
        <template>{template}</template>

        Consider the following information:
        <attorneys>{[x.name for x in self.input.attorneys or []]}</attorneys>
        <resolution-date>{self.input.request_date}</resolution-date>
        <case-title>{self.input.case_title}</case-title>
        <case-role>{self.input.case_role}</case-role>
        <demand-text>{demand_text}</demand-text>
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, aside from response_body, adjust text around them so it reads naturally.
        - Return one or more paragraphs of text.
        """
        if self.input.suggestion:
            prompt += f"""
            Consider that an assistant has come up with a strong suggestion, use it to guide your response_body section:
            <suggestion>{self.input.suggestion}</suggestion>
            """
        response: Response = self.generator_llm.invoke(prompt)
        return response.text or "Por este acto, vengo en dar cumplimiento a lo ordenado."
    
    def _generate_request(self) -> str:
        template = "POR TANTO;\n\nA US. SOLICITO: Ruego a US. tener por cumplido lo ordenado."
        if not self.input.request_date and not self.input.request:
            return template
        if self.input.request_date:
            template = "POR TANTO;\n\nA US. SOLICITO: Ruego a US. tener por cumplido lo ordenado con fecha {request_date (format_example: 10 de febrero de 2021)}."
        if self.input.request:
            template = template[:-1] + ", y {request_summary (format_example: en su mérito, se tenga por interpuesta la demanda presentada por esta parte.)}."
        prompt = f"""
        Generate a short legal request in {self.locale}, to do so, consider the following template:
        <template>{template}</template>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Replace and adjust only placeholder values and text around them to keep proper grammar and casing.
        """
        if self.input.request_date:
            prompt += f"- As request_date, consider this date value: <date>{self.input.request_date}</date>"
        if self.input.request:
            prompt += f"- As request_summary, consider this information: <info>{self.input.request}</info>"
        request: Response = self.generator_llm.invoke(prompt)
        return request.text or "POR TANTO;\n\nA US. SOLICITO: Ruego a US. tener por cumplido lo ordenado."
