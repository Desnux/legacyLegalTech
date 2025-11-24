import time

from models.pydantic import MissingPaymentDocumentType
from services.v2.document.base import BaseGenerator, Metrics, Response
from services.v2.document.bill import BillInformation
from services.v2.document.promissory_note import PromissoryNoteInformation
from .models import (
    MissingPaymentArgumentGeneratorInput,
    MissingPaymentArgumentGeneratorOutput,
    MissingPaymentArgumentReason,
    MissingPaymentArgumentStructure,
)


COMMON_INSTRUCTIONS = """
When answering:
- Generate your response in es_ES.
- Consider that the information may match template placeholders values regardless of differences in plurality.
- Adjust the inserted information and/or the text around it to ensure the result reads naturally, for example when dealing with plural or singular entities.
- Adjust casing for reason an add connecting words arount it to ensure the result reads naturally alongise the rest of the content.
- Use titlecase when filling up names, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
- Do not use fake or example data to replace placeholders, use only real data provided inside the information tags.
- If you are missing information to replace a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
- If amount_currency is not CLP, you must indicate the currency type after amount or pending_amount, for example in the case of USD: $1.000.000.- USD
- Add honorifics to names of people other than attorneys, such as don or doña, exclude them from names of groups, businesses or institutions.
"""


class MissingPaymentArgumentGenerator(BaseGenerator):
    """Missing payment argument generator."""

    def __init__(self, input: MissingPaymentArgumentGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        self.reasoner = self._create_structured_generator(MissingPaymentArgumentReason)
        self.structured_reason: MissingPaymentArgumentReason | None = self.input.structured_reason
        
    def generate(self) -> MissingPaymentArgumentGeneratorOutput:
        """Generate missing payment argument structure from input."""
        structure: MissingPaymentArgumentStructure | None = None
        metrics = Metrics(label="MissingPaymentArgumentGenerator.generate")
        start_time = time.time()

        if document := self.input.document:
            if not self.structured_reason:
                if reason := self.input.reason:
                    self.structured_reason = self.extract_reason(reason)
                    metrics.llm_invocations += 1

            match document_type := self.input.document_type:
                case MissingPaymentDocumentType.BILL:
                    argument: Response = self.generator.invoke(self._create_bill_prompt(document))
                    structure = MissingPaymentArgumentStructure(document_type=document_type, argument=argument.output)
                case MissingPaymentDocumentType.PROMISSORY_NOTE:
                    argument: Response = self.generator.invoke(self._create_promissory_note_prompt(document))
                    structure = MissingPaymentArgumentStructure(document_type=document_type, argument=argument.output)
        if structure:
            structure.normalize()
            metrics.llm_invocations += 1

        metrics.time = round(time.time() - start_time, 4)
        return MissingPaymentArgumentGeneratorOutput(
            metrics=metrics,
            structured_output=structure if structure is not None else None,
            structured_reason=self.structured_reason,
        )
    
    def extract_reason(self, reason: str) -> MissingPaymentArgumentReason:
        """Extracts a structured reason from raw text."""
        return self.reasoner.invoke(self._create_reason_prompt(reason))
    
    def _create_bill_template(self) -> str:
        lines: list[str] = []
        if self.input.over_creditor:
            lines.append(
                (
                    "La empresa {creditor.name}, con RUT {creditor.identifier}, ha cedido a mi representado, "
                    "{over_creditor.name}, la factura electrónica Nº {identifier}, emitida con fecha {creation_date}, "
                    "por un monto total de ${amount}. -"
                )
            )
        else:
            lines.append(
                (
                    "La empresa {creditor.name}, con RUT {creditor.identifier}, ha emitido la factura electrónica Nº "
                    "{identifier} con fecha {creation_date}, por un monto total de ${amount}. -"
                )
            )
        lines.extend([
            (
                "Cabe señalar que la factura cedida cumple con lo dispuesto en la Ley 19.983, por lo que, para "
                "efectos de preparar la vía ejecutiva, procede que se notifique judicialmente a su obligado al pago."
            ),
            (
                "Asimismo, la cesión de las facturas fue debidamente notificada al deudor, {debtor.name}, tal "
                "como consta en el certificado de anotación en el Registro Público Electrónico de Transferencia "
                "de Créditos, llevado por el Servicio de Impuestos Internos."
            ),
            (
                "Sin embargo, el deudor {reason}. Por lo tanto, además del precio nominal de la prestación "
                "adeudada, que asciende a ${pending_amount}. -, aquel deberá pagar los intereses correspondientes, "
                "a contar de la mora o simple retardo en el pago del precio, y hasta la fecha de pago íntegro y "
                "total de lo adeudado."
            ),
        ])
        return "\n\n".join(lines)

    def _create_bill_prompt(self, bill: BillInformation) -> str:
        information = {**bill.get_simple_dict()}
        if argument_reason := self.structured_reason:
            information["reason"] = argument_reason.reason
            information["pending_amount"] = argument_reason.pending_amount or bill.amount,
        else:
            information["reason"] = "NO DIO PAGO"
            information["pending_amount"] = bill.amount,
        if over_creditor := self.input.over_creditor:
            information["over_creditor"] = {"name": over_creditor.name}
        prompt = f"""
        Your task is to generate a legal argument for the plaintiffs about missing payments related to a bill.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template and expected filled placeholder values format, you are allowed to modify the template as you see fit:
        <filled-values-format-example>
        creditor.identifier: 12.345.678-9
        creation_date: 01 de diciembre de 2021
        amount: 14.694.905
        pending_amount: 14.694.905
        </filled-values-format-example>
        <template>{self._create_bill_template()}</template>

        {COMMON_INSTRUCTIONS}
        """
        return prompt
    
    def _create_promissory_note_template(self) -> str:
        lines: list[str] = []
        lines.extend([
            (
                "Pagaré N°{identifier}, suscrito a la orden de {creditor.name}, con fecha {creation_date}, "
                "por la suma de ${amount}.-, que la parte demandada declaró haber recibido en préstamos en "
                "dineros en efectivo a su entera satisfacción y conformidad, obligándose a pagarlo conjuntamente "
                "con los intereses devengados, en {payment_installments} cuotas {payment_frequency}, iguales y "
                "sucesivas de ${amount_per_installment}.-, con excepción de la última cuota, que sería por la "
                "suma de ${amount_last_installment}.-, con vencimiento los días {due_payment_day} de cada "
                "{payment_frequency}, a contar de {first_installment_date}, y hasta {last_installment_date}."
            ),
            (
                "Se estipuló que el capital adeudado devengaría una tasa de interés del {interest_rate}% "
                "{interest_rate_frequency}, calculado en base a un año de {interest_rate_base_days} días y "
                "vencidos y el número días efectivamente transcurridos, el que regirá a contar de la fecha de "
                "suscripción y por todo el periodo de la obligación, pagaderos conjuntamente con el capital adeudado."
            ),
            (
                "Asimismo se pactó, que en caso de mora o simple retardo en el pago de capital o intereses, "
                "la tasa de interés se elevará al interés máximo convencional que la ley permita estipular para "
                "operaciones de crédito en moneda nacional, vigente a esta fecha o a la época de la mora o retardo "
                "a elección del acreedor, desde el momento del retardo y hasta el pago efectivo."
            ),
            (
                "Además se estipuló que el Banco podría hacer exigible el pago total de la suma de la deuda o "
                "del saldo a que ésta se hallara reducida, considerando la presente obligación como de plazo "
                "vencido, en caso de mora o simple retardo en el pago de una cualquiera de las cuotas en que se "
                "dividió la obligación, sea de capital y/o intereses, sean consecutivas o no, sin perjuicio de los "
                "demás derechos del acreedor."
            ),
        ])
        if self.input.document and self.input.document.co_debtors:
            lines.append("En dicho pagaré, se constituyó en aval, fiador y codeudor solidario, {co_debtor.name}, ya individualizado.")
        lines.extend([
            (
                "Por último, se pactó que todas las obligaciones que emanan del pagaré serán solidarias "
                "para el o los suscriptores, avalistas y demás obligados al pago y serán indivisibles para sus "
                "herederos y/o sucesores conforme a los artículos 1526 número 4 y 1528 del Código Civil. Además, "
                "cabe señalar que en el pagaré se liberó expresamente a {creditor.name} de la obligación de protesto."
            ),
            (
                "Es del caso que el deudor {reason}, razón por la cual y de acuerdo a lo estipulado vengo en "
                "hacer exigible, a contar de la fecha la presentación de la presente demanda, el total de la "
                "obligación insoluta, la que asciende a la suma de ${pending_amount}.-, de los cuales, "
                "${capital_amount}.- corresponde a capital, ${interest_amount}.- corresponde a intereses, y "
                "${debt_amount}.- corresponde a recargo por mora."
            ),
            (
                "La firma de los suscriptores del pagaré antes singularizado se encuentra autorizada por "
                "Notario Público, razón por la cual dicho instrumento tiene mérito ejecutivo respecto de todos "
                "sus obligados, y siendo las obligación líquida, actualmente exigible y estando la acción "
                "ejecutiva vigente, procede se despache mandamiento de ejecución y embargo en su contra."
            ),
        ])
        return "\n\n".join(lines)

    def _create_promissory_note_prompt(self, promissory_note: PromissoryNoteInformation) -> str:
        information = {**promissory_note.get_simple_dict()}
        if argument_reason := self.structured_reason:
            information = {
                **information,
                **argument_reason.model_dump(),
                "pending_amount": argument_reason.pending_amount or promissory_note.amount,
            }
        else:
            information["reason"] = "NO DIO PAGO"
            information["pending_amount"] = promissory_note.amount,
        prompt = f"""
        Your task is to generate a legal argument for the plaintiffs about missing payments related to a promissory note.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template and expected filled placeholder values format, you are allowed to modify the template as you see fit:
        <filled-values-format-example>
        identifier (numeric): a plazo N° 6300179957
        identifier (name): boleta garantía en pesos
        creation_date: 01 de diciembre de 2021
        amount: 14.694.905
        amount_installment: 14.694.905
        first_installment_date: 01 de diciembre de 2021
        last_installment_date: 01 de diciembre de 2021
        interest_rate: 8,3
        pending_amount: 14.694.905
        capital_amount: 14.694.905
        interest_amount: 14.694.905
        debt_amount: 14.694.905
        </filled-values-format-example>
        <template>{self._create_promissory_note_template()}</template>

        {COMMON_INSTRUCTIONS}
        """
        return prompt  

    def _create_reason_prompt(self, source: str) -> str:
        prompt = f"""
        Your task is to extract information from the following human written text source about a reason to argue about a missing payment:
        <source>{source}</source>

        When answering:
        - Extract reason in es_ES.
        - Assign null to non-specified amounts.
        - Do not return fake or example information, only use content inside source tags.
        """
        return prompt
