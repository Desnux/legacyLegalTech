import time

from services.v2.document.base import BaseGenerator, Metrics, Response
from .models import DemandTextMainRequestGeneratorInput, DemandTextMainRequestGeneratorOutput, DemandTextMainRequestStructure


class DemandTextMainRequestGenerator(BaseGenerator):
    """Demand text main request generator."""

    def __init__(self, input: DemandTextMainRequestGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        
    def generate(self) -> DemandTextMainRequestGeneratorOutput:
        """Generate main request structure from input."""
        metrics = Metrics(label="DemandTextMainRequestGenerator.generate")
        start_time = time.time()

        response: Response = self.generator.invoke(self._create_prompt())
        structure = DemandTextMainRequestStructure(content=response.output)
        structure.normalize()
        metrics.llm_invocations += 1

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextMainRequestGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)
    
    def _create_content(self) -> str:
        lines: list[str] = [
            "POR TANTO, en mérito de lo expuesto, y de conformidad a lo prescrito en los Arts. 434 y siguientes del Código de Procedimiento Civil,",
        ]

        # Request line
        debtors = []
        for debtor in self.input.debtors or []:
            if not debtor.name:
                continue
            if legal_representatives := debtor.legal_representatives:
                representatives = [representative.name for representative in legal_representatives if representative.name]
                if len(representatives) == 1:
                    debtors.append(f"en contra de {debtor.name}, representada por {representatives[0]}, en su calidad de deudor principal")
                    continue
                elif len(representatives) > 0:
                    debtors.append(f"en contra de {debtor.name}, representada por {', '.join(representatives[:-1])} y {representatives[-1]}, en su calidad de deudor principal")
                    continue
            debtors.append(f"en contra de {debtor.name}, en su calidad de deudor principal")
        if len(debtors) == 1:
            current_line = f"RUEGO A US. tener por interpuesta la presente demanda ejecutiva {debtor[0]}."
        elif len(debtors) > 0:
            current_line = f"RUEGO A US. tener por interpuesta la presente demanda ejecutiva {', '.join(debtors[:-1])} y {debtors[-1]}."
        else:
            current_line = "RUEGO A US. tener por interpuesta la presente demanda ejecutiva."
        lines.append(current_line)

        return "\n\n".join(lines)

    def _create_prompt(self) -> str:
        information = {
            "amount_in_dispute_as_number": self.input.amount,
            "amount_in_dispute_as_words_read_aloud": self.input.amount,
            "amount_currency": self.input.amount_currency,
            "debtors": list(map(
                lambda x: {
                    "name": x.name, "legal_representatives": list(map(lambda x: {"name": x.name}, x.legal_representatives or [])),
                },
                self.input.debtors or [],
            )),
            "co_debtors": list(map(lambda x: {"name": x.name}, self.input.co_debtors or [])),
        }
        prompt = f"""
        Your task is to generate the main request of a demand about missing payments.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template and expected filled placeholder values format, you are allowed to modify the template as you see fit:
        <filled-values-format-example>
        amount_in_dispute_as_number: 105.055.000
        amount_in_dispute_as_words_read_aloud: ciento cinco millones cincuenta y cinco mil pesos
        </filled-values-format-example>
        <template>{self._create_template()}</template>

        When answering:
        - Generate your response in es_ES.
        - Consider that the information may match template placeholders values regardless of differences in plurality.
        - Adjust the inserted information and/or the text around it to ensure the result reads naturally, for example when dealing with plural or singular entities.
        - Use titlecase when filling up names and addresses, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - Do not use fake or example data to replace placeholders, use only real data provided inside the information tags.
        - If you are missing information to replace a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
        - If amount_currency is not CLP, you must indicate the currency type after amount or pending_amount, for example in the case of USD: $1.000.000.- USD
        - Add honorifics to names of people other than attorneys, such as don or doña, exclude them from names of groups, businesses or institutions.
        """
        return prompt

    def _create_template(self) -> str:
        lines: list[str] = [
            "POR TANTO, en mérito de lo expuesto, y de conformidad a lo prescrito en los Arts. 434 y siguientes del Código de Procedimiento Civil,",
        ]
        if self.input.co_debtors:
            lines.append("RUEGO A US. tener por interpuesta la presente demanda ejecutiva en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal, y en contra de {co_debtor.name}, en su calidad de aval, fiador y codeudor solidario, ambos ya individualizados, ordenando se despache mandamiento de ejecución y embargo en su contra por la suma total de ${amount_in_dispute_as_number}.- ({amount_in_dispute_as_words_read_aloud}), más los intereses que correspondan, ordenando se siga adelante con esta ejecución hasta hacer a mi representado entero y cumplido pago de lo adeudado, con costas.")
        else:
            lines.append("RUEGO A US. tener por interpuesta la presente demanda ejecutiva en contra de {debtor.name}, representada por {debtor.legal_representative.name}, en su calidad de deudor principal, ya individualizado, ordenando se despache mandamiento de ejecución y embargo en su contra por la suma total de ${amount_in_dispute_as_number}.- ({amount_in_dispute_as_words_read_aloud}), más los intereses que correspondan, ordenando se siga adelante con esta ejecución hasta hacer a mi representado entero y cumplido pago de lo adeudado, con costas.",)
        return "\n\n".join(lines)
