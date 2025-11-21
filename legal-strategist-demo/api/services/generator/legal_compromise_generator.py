import logging
from datetime import datetime

from pydantic import BaseModel, Field

from models.pydantic import (
    JudicialCollectionDemandTextStructure,
    LegalCompromise,
    LegalCompromiseInput,
    LegalCompromiseRequest,
    Locale,
)
from util import int_to_roman, int_to_ordinal
from .base_generator import BaseGenerator


class AdditionalRequests(BaseModel):
    requests: list[LegalCompromiseRequest] | None = Field(None, description="Additional requests to include in the compromise, if any")


class Response(BaseModel):
    text: str | None = Field(None, description="Generation output")


class CompromiseTerms(BaseModel):
    terms: list[str] | None = Field(None, description="List of terms of the compromise")


class LegalCompromiseGenerator(BaseGenerator):
    def __init__(self, input: LegalCompromiseInput, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(Response)
        self.requests_llm = self.get_structured_generator(AdditionalRequests)
        self.terms_llm = self.get_structured_generator(CompromiseTerms)
        self.locale = locale
    
    def generate(self, demand_text: JudicialCollectionDemandTextStructure) -> LegalCompromise:
        demand_text_content = demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"})
        court = self._generate_court()
        opening = self._generate_opening()
        compromise_terms = self._generate_compromise_terms(demand_text_content)
        main_request = self._generate_main_request()

        if self.input.suggestion and self.input.secondary_requests is None:
            try:
                self._self_generate_additional_requests(compromise_terms)
            except Exception as e:
                logging.warning(f"Could not self generate additional requests for legal compromise: {e}")

        summary = self._generate_summary()
        additional_requests = self._generate_additional_requests()

        return LegalCompromise(
            summary=summary,
            court=court,
            opening=opening,
            compromise_terms=compromise_terms,
            main_request=main_request,
            additional_requests=additional_requests,
        )
    
    def _generate_summary(self) -> str | None:
        segments: list[str] = []
        secondary_segments: list[str] = []
        affix = "OTROSÍ"
        segments.append("EN LO PRINCIPAL: AVENIMIENTO")

        for secondary_request in self.input.secondary_requests or []:
            secondary_segments.append(secondary_request.to_localized_string(self.locale))
        if len(secondary_segments) > 0:
            numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(secondary_segments)]
            segments.extend(numbered_segments)
        if len(segments) == 0:
            return None
        return "; ".join(segments)

    def _generate_court(self) -> str:
        if self.input.court_city and self.input.court_number:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()} ({self.input.court_number}º)"
        if self.input.court_city:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()}"
        return "S.J.L."
    
    def _generate_opening(self) -> str:
        template = """
        {sponsoring_attorney.name}, abogado, por el ejecutante, {plaintiff.name}, en los autos caratulados “{case_title}”, ROL {case_role}, a US., con respeto digo:\n\n
        Que, con objeto de poner término al presente procedimiento, vengo a presentar los siguientes términos de avenimiento, para aprobación de este Tribunal:
        """
        if self.input.defendant_attorneys:
            template = """
            {sponsoring_attorney.name}, abogado, por el ejecutante, {plaintiff.name}; y {defendant_attorney.name}, abogado, por los ejecutados, {defendant.name}, en los autos caratulados “{case_title}”, ROL {case_role}, a US., respetuosamente decimos:\n\n
            Que, con objeto de poner término al presente procedimiento, las partes vienen a presentar los siguientes siguientes términos de avenimiento, para aprobación de este Tribunal:
            """
        prompt = f"""
        Generate an opening for a compromise request in a legal case, to do so, fill the following template in {self.locale}, adjust, add, or remove information where needed:
        <template>{template}</template>

        Consider the following information:
        <plaintiffs>{[x.name for x in self.input.plaintiffs or []]}</plaintiffs>
        <sponsoring-attorneys>{[x.name for x in self.input.sponsoring_attorneys or []]}</sponsoring-attorneys>
        <defendants>{[x.name for x in self.input.defendants or []]}</defendants>
        <defendant-attorneys>{[x.name for x in self.input.defendant_attorneys or []]}</defendant-attorneys>
        <case-title>{self.input.case_title}</case-title>
        <case-role>{self.input.case_role}</case-role>
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
        """
        response: Response = self.generator_llm.invoke(prompt)
        return response.text or "Por este acto, vengo a presentar los siguientes términos de avenimiento, para aprobación de este Tribunal:"

    def _generate_compromise_terms(self, demand_text: str) -> str | None:
        prompt = f"""
        As an assistant to the plaintiffs of a legal case about judicial collection, your task is to generate three valid terms for a compromise that would help close the case, in {self.locale}.

        Consider the contents of the original demand text redacted by the plaintiffs:
        <demand-text>{demand_text}</demand-text>

        Do also consider the following information:
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>
        <sponsoring-attorneys>{[x.model_dump_json() for x in self.input.sponsoring_attorneys or []]}</sponsoring-attorneys>
        <plaintiffs>{[x.model_dump_json() for x in self.input.plaintiffs or []]}</plaintiffs>

        Your first term must be related to the total amount to pay, either in one payment or through many installments, for example:
        <total-amount-term>
        La demandada pagará la suma total de $187.500.- (ciento ochenta y siete mil quinientos pesos), por concepto de deuda capital, en los siguientes términos:
        \n- Un abono inicial por la suma de $30.000.- (treinta mil pesos).
        \n- Una segunda y tercera cuota, cada una de ellas por la suma de $30.000.- (treinta mil pesos), más los intereses correspondientes, pagadera los días 06 de enero de 2023, y 03 de febrero de 2023.
        \n- Cada una de las cuotas se pagará en su equivalente en pesos, a la fecha de pago efectivo.
        </total-amount-term>

        Your second term must be related to how to pay the amount, for example:
        <how-to-pay-term>
        Todos los pagos se efectuarán mediante depósito o transferencia electrónica, en la cuenta cuyo titular es {{plaintiff.name}}, RUT N° {{plaintiff.identifier}}, enviando copia a las casillas de correo {{plaintiff.email}} y {{sponsoring_attorney.email}}.
        </how-to-pay-term>

        Your third term must be related to what happens if the compromise were to be broken, for example:
        <breakup-term>
        Del mismo modo, las partes estipulan que no verificado el pago en la fecha y condiciones estipuladas, {{plaintiff.name}} podrá demandar el cumplimiento del avenimiento en el presente juicio o iniciar una ejecución nueva
        </breakup-term>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - If an amount is not CLP, you must indicate the currency type after the amount, for example in the case of USD: $1.000.000.- USD"
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
        - Return a list of three strings, subitems must be included inside its parent, separated by double newlines.
        """
        if self.input.suggestion:
            prompt += f"""
            Consider that an assistant has come up with a strong suggestion, use it to guide your terms:
            <suggestion>{self.input.suggestion}</suggestion>
            """
        response: CompromiseTerms = self.terms_llm.invoke(prompt)
        if not response.terms:
            return None
        segments = response.terms
        segments.insert(2, "Las partes estipulan que, solo una vez cumplido este avenimiento, y el pago del total de las cuotas estipuladas, se dará término al juicio.")
        segments.append("Como consecuencia de los acuerdos antes indicados, las partes litigantes renuncian al ejercicio de las defensas empleadas, y de las que en derecho pueden hacer valer en esta causa, otorgándose el más completo y total finiquito, salvo el que emane del incumplimiento del presente avenimiento")
        numbered_segments = [f"{int_to_roman(i + 1)}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _generate_main_request(self) -> str:
        if self.input.defendant_attorneys and self.input.sponsoring_attorneys:
            return "POR TANTO,\n\nROGAMOS A US. aprobar los términos del presente avenimiento sometido a su aprobación."
        return "POR TANTO,\n\nRUEGO A US. aprobar los términos del presente avenimiento sometido a su aprobación."

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        affix = "OTROSÍ"
        plural = self.input.sponsoring_attorneys and self.input.defendant_attorneys
        for secondary_request in self.input.secondary_requests or []:
            segments.append(secondary_request.to_description_string(self.locale, plural))
        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _self_generate_additional_requests(self, compromise_terms: str | None = None) -> None:
        requests_descriptions = "\n".join(
            f"- <request-type><value>{item.value}</value><description>{item.to_description_string(Locale.EN_US, self.input.defendant_attorneys)}</description></request-type>"
            for item in LegalCompromiseRequest
        )
        prompt = f"""
        In the context of a legal case, consider the following list of request types that attorneys can raise when coming up with a compromise:
        {requests_descriptions}

        Given this suggestion:
        <suggestion>{self.input.suggestion}</suggestion>
        """
        if compromise_terms:
            prompt += f"""
            As well of the compromise terms already redacted:
            <compromise-terms>{compromise_terms}</compromise-terms>
            """
        prompt += f"""
        Your job is to indicate the request or requests that could be included in the document, if any, by their value field.
        """
        response: AdditionalRequests = self.requests_llm.invoke(prompt)
        if response.requests:
            self.input.secondary_requests = response.requests
