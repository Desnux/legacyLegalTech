import time

from models.pydantic import Locale
from services.v2.document.base import BaseGenerator, Metrics, Response
from util import int_to_ordinal
from .models import (
    WithdrawalGeneratorInput,
    WithdrawalGeneratorOutput,
    WithdrawalStructure,
)


class WithdrawalGenerator(BaseGenerator):
    """Withdrawal generator."""

    def __init__(self, input: WithdrawalGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        self.use_plural = len(input.sponsoring_attorneys or []) > 1
        self.legal_article = input.legal_article if input.legal_article else "148 del Código de Procedimiento Civil"
    
    def generate(self) -> WithdrawalGeneratorOutput:
        """Generate withdrawal structure from input."""
        metrics = Metrics(label="WithdrawalGenerator.generate")
        start_time = time.time()

        header = self._generate_header()
        summary = self._generate_summary()
        court = self._generate_court()

        content = self._generate_content()
        metrics.llm_invocations += 1

        main_request = self._generate_main_request()
        metrics.llm_invocations += 1

        structure = WithdrawalStructure(
            header=header,
            summary=summary,
            court=court,
            content=content,
            main_request=main_request,
        )
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return WithdrawalGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)
    
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
        segments: list[str] = ["EN LO PRINCIPAL: SE DESISTE DE DEMANDA EN LOS TÉRMINOS QUE INDICA"]
        secondary_segments: list[str] = []
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

    def _generate_content(self) -> str | None:
        response: Response = self.generator.invoke(self._create_content_prompt())
        return response.output if response else None
    
    def _create_content_prompt(self) -> str:
        information = {
            "sponsoring_attorneys": list(map(lambda x: {"name": x.name}, self.input.sponsoring_attorneys or [])),
            "debtors": list(map(
                lambda x: {
                    "name": x.name, "legal_representatives": list(map(lambda x: {"name": x.name}, x.legal_representatives or [])),
                },
                self.input.debtors or [],
            )),
            "co_debtors": list(map(lambda x: {"name": x.name}, self.input.co_debtors or [])),
        }
        prompt = f"""
        Your task is to generate the content of a withdrawal request from a case, in the role of the plaintiffs.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template, you are allowed to modify the template as you see fit:
        <template>{self._create_content_template()}</template>

        {self._create_common_instructions()}
        """
        return prompt

    def _create_content_template(self) -> str:
        text: list[str] = [
            "abogados" if self.use_plural else "abogado",
            "digo" if self.use_plural else "decimos",
            "venimos en desistirnos" if self.use_plural else "vengo en desistirme",
        ]
        opening = f"{text[0]}, por el ejecutante, en estos autos ejecutivos"
        if case_title := self.input.case_title:
            opening += f" caratulados “{case_title}”"
        if case_role := self.input.case_role:
            opening += f" , Rol {case_role}"
        lines: list[str] = []
        if self.input.sponsoring_attorneys:
            lines.append("{sponsoring_attorney.name}, " + opening + f" , a US. respetuosamente {text[1]}:")
        else:
            lines.append("En mi calidad de " + opening + f" , a US. respetuosamente {text[1]}:")
        followup = f"En uso del derecho que nos confiere el artículo {self.legal_article}, {text[2]} de la demanda ejecutiva interpuesta"
        if self.input.debtors and self.input.co_debtors:
            lines.append(followup + " en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal, y en contra de {co_debtor.name}, en su calidad de aval, fiador y codeudor solidario.")
        elif self.input.debtors:
            lines.append(followup + "en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal.")
        elif self.input.co_debtors:
           lines.append(followup + " en contra de {co_debtor.name}, en su calidad de aval, fiador y codeudor solidario de la demandada principal.")
        else:
            lines.append(f"{followup}.")
        return "\n\n".join(lines)

    def _generate_main_request(self) -> str | None:
        response: Response = self.generator.invoke(self._create_main_request_prompt())
        if not response.output:
            return None
        return "\n\n".join(["POR TANTO,", response.output])

    def _create_main_request_prompt(self) -> str:
        information = {
            "debtors": list(map(
                lambda x: {
                    "name": x.name, "legal_representatives": list(map(lambda x: {"name": x.name}, x.legal_representatives or [])),
                },
                self.input.debtors or [],
            )),
            "co_debtors": list(map(lambda x: {"name": x.name}, self.input.co_debtors or [])),
        }
        prompt = f"""
        Your task is to generate the main request of a withdrawal from a case, in the role of the plaintiffs.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template, you are allowed to modify the template as you see fit:
        <template>{self._create_main_request_template()}</template>

        {self._create_common_instructions()}
        """
        return prompt

    def _create_main_request_template(self) -> str:
        text: list[str] = [
            "ROGAMOS A US., " if self.use_plural else "RUEGO A US., ",
        ]
        opening = text[0] + f"en mérito de lo dispuesto en el artículo {self.legal_article}, se sirva tener a esta parte por desistida de la demanda ejecutiva"
        lines: list[str] = []
        if self.input.debtors and self.input.co_debtors:
            lines.append(opening + " en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal, y en contra de {co_debtor.name}, en su calidad de aval, fiador y codeudor solidario.")
        elif self.input.debtors:
            lines.append(opening + "en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal.")
        elif self.input.co_debtors:
           lines.append(opening + " en contra de {co_debtor.name}, en su calidad de aval, fiador y codeudor solidario de la demandada principal.")
        else:
            lines.append(f"{opening}.")
        return "\n\n".join(lines)
