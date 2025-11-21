import time
from datetime import datetime

from models.pydantic import DefendantType, Locale
from services.v2.document.base import BaseGenerator, Metrics, Response, ResponseList
from util import int_to_ordinal, int_to_roman
from .models import (
    CompromiseGeneratorInput,
    CompromiseGeneratorOutput,
    CompromiseStructure,
)


class CompromiseGenerator(BaseGenerator):
    """Compromise generator."""

    def __init__(self, input: CompromiseGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        self.generator_list = self._create_structured_generator(ResponseList)
        self.use_defendant_plural = len(input.defendant_attorneys or []) > 1
        self.use_plaintiff_plural = len(input.sponsoring_attorneys or []) > 1
        self.use_multiple_parties = len(input.sponsoring_attorneys or []) > 1 and len(input.defendant_attorneys or []) > 1
    
    def generate(self) -> CompromiseGeneratorOutput:
        """Generate withdrawal structure from input."""
        metrics = Metrics(label="WithdrawalGenerator.generate")
        start_time = time.time()

        header = self._generate_header()
        summary = self._generate_summary()
        court = self._generate_court()
        main_request = self._generate_main_request()
        additional_requests = self._generate_additional_requests()

        opening = self._generate_opening()
        metrics.llm_invocations += 1

        compromise_terms = self._generate_compromise_terms()
        metrics.llm_invocations += 1

        structure = CompromiseStructure(
            header=header,
            summary=summary,
            court=court,
            opening=opening,
            compromise_terms=compromise_terms,
            main_request=main_request,
            additional_requests=additional_requests,
        )
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return CompromiseGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)
    
    def _generate_header(self) -> str | None:
        text: str = ""
        if self.input.court_number and self.input.court_city:
            text += f"JUZGADO : {self.input.court_number}º CIVIL DE {self.input.court_city.upper()}"
        elif self.input.court_city:
            text += f"JUZGADO : CIVIL DE {self.input.court_city.upper()}"
        if self.input.case_role:
            text += f"\nCAUSA ROL : {self.input.case_role.upper()}"
        if self.input.case_title:
            text += f"\nCARATULADO : {self.input.case_title.upper()}"
        text += f"\nCUADERNO : PRINCIPAL"
        if len(text) == 0:
            return None
        return text
    
    def _generate_summary(self) -> str | None:
        segments: list[str] = ["EN LO PRINCIPAL: AVENIMIENTO"]
        secondary_segments: list[str] = []
        for secondary_request in self.input.secondary_requests or []:
            secondary_segments.append(secondary_request.to_localized_string())
        if len(secondary_segments) > 0:
            numbered_segments = [f"{int_to_ordinal(i + 1, Locale.ES_ES)} OTROSÍ: {segment}" for i, segment in enumerate(secondary_segments)]
            segments.extend(numbered_segments)
        if len(segments) == 0:
            return None
        return "; ".join(segments)
    
    def _generate_court(self) -> str | None:
        text: str = "S.J.L."
        if len(text) == 0:
            return None
        return text

    def _generate_main_request(self) -> str:
        if self.use_defendant_plural or self.use_plaintiff_plural or self.use_multiple_parties:
            return "POR TANTO,\n\nROGAMOS A US. aprobar los términos del presente avenimiento sometido a su aprobación."
        return "POR TANTO,\n\nRUEGO A US. aprobar los términos del presente avenimiento sometido a su aprobación."

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        plural = self.input.sponsoring_attorneys and self.input.defendant_attorneys
        for secondary_request in self.input.secondary_requests or []:
            segments.append(secondary_request.to_description_string(plural))
        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, Locale.ES_ES)} OTROSÍ: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _generate_compromise_terms(self) -> str | None:
        response: ResponseList = self.generator_list.invoke(self._create_compromise_terms_prompt())
        if not response.output:
            return None
        segments = response.output
        segments.insert(2, "Las partes estipulan que, solo una vez cumplido este avenimiento, y el pago del total de las cuotas estipuladas, se dará término al juicio.")
        segments.append("Como consecuencia de los acuerdos antes indicados, las partes litigantes renuncian al ejercicio de las defensas empleadas, y de las que en derecho pueden hacer valer en esta causa, otorgándose el más completo y total finiquito, salvo el que emane del incumplimiento del presente avenimiento")
        numbered_segments = [f"{int_to_roman(i + 1)}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)
    
    def _create_compromise_terms_prompt(self) -> str:
        information = {
            "current_date": datetime.today().strftime("%Y-%m-%d"),
            "plaintiffs": list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.input.plaintiffs or [])),
            "sponsoring_attorneys": list(map(lambda x: {"name": x.name}, self.input.sponsoring_attorneys or [])),
            "demand_text": self.input.demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"}) if self.input.demand_text else None,
        }
        prompt = f"""
        Your task is to generate the compromise terms of a settlement request in order to end a legal case.

        In order to do this, consider the following information:
        <information>{information}</information>

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

        {self._create_common_instructions()}
        - Return a list of three strings, subitems must be included inside its parent, separated by double newlines.
        """
        return prompt

    def _generate_opening(self) -> str | None:
        response: Response = self.generator.invoke(self._create_opening_prompt())
        return response.output if response else None
    
    def _create_opening_prompt(self) -> str:
        information = {
            "sponsoring_attorneys": list(map(lambda x: {"name": x.name}, self.input.sponsoring_attorneys or [])),
            "defendant_attorneys": list(map(lambda x: {"name": x.name}, self.input.defendant_attorneys or [])),
            "debtors": list(map(lambda x: {"name": x.name}, filter(lambda x: x.type == DefendantType.DEBTOR, self.input.defendants or []))),
            "plaintiffs": list(map(lambda x: {"name": x.name}, self.input.plaintiffs or [])),
        }
        prompt = f"""
        Your task is to generate the opening of a settlement request in order to end a legal case.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template, you are allowed to modify the template as you see fit:
        <template>{self._create_opening_template()}</template>

        {self._create_common_instructions()}
        """
        return prompt

    def _create_opening_template(self) -> str:
        text: list[str] = [
            "abogados" if self.use_plaintiff_plural else "abogado",
            "abogados" if self.use_defendant_plural else "abogado",
            "digo" if self.use_defendant_plural or self.use_plaintiff_plural or self.use_multiple_parties else "decimos",
            "venimos" if self.use_plaintiff_plural or self.use_defendant_plural else "vengo",
        ]
        plaintiff_segment = ", por el ejecutante, {plaintiff.name}" if self.input.plaintiffs else ", por el ejecutante"
        defendant_segment = ", por los ejecutados, {defendant.name}" if self.input.plaintiffs else ", por los ejecutados"
        if self.use_multiple_parties:
            opening = "{sponsoring_attorney.name}, " + text[0] + plaintiff_segment + "; y {defendant_attorney.name}, " + text[1] + ", por los ejecutados, {defendant.name} en estos autos ejecutivos"
        elif self.input.sponsoring_attorneys:
            opening = "{sponsoring_attorney.name}, " + text[0] + plaintiff_segment + ", en estos autos ejecutivos"
        elif self.input.defendant_attorneys:
            opening = text[1] + defendant_segment + ", en estos autos ejecutivos"
        else:
            opening = "En mi calidad de abogado, en estos autos ejecutivos"
        if case_title := self.input.case_title:
            opening += f" caratulados “{case_title}”"
        if case_role := self.input.case_role:
            opening += f" , Rol {case_role}"
        lines: list[str] = [opening + f" , a US. respetuosamente {text[2]}:"]
        if self.use_multiple_parties:
            lines.append("Que, con objeto de poner término al presente procedimiento, las partes vienen a presentar los siguientes términos de avenimiento, para aprobación de este Tribunal:")
        else:
            lines.append(f"Que, con objeto de poner término al presente procedimiento, {text[3]} a presentar los siguientes términos de avenimiento, para aprobación de este Tribunal:")
        return "\n\n".join(lines)
