from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field

from models.pydantic import CurrencyType
from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class Article5Presumption(str, Enum):
    LETTER_B = "letter_b"
    LETTER_C = "letter_c"
    LETTER_D = "letter_d"
    LETTER_G = "letter_g"
    LETTER_H = "letter_h"

    def get_analysis_description(self, idx: int, context: dict | None = None) -> str:
        connectors = [
            "Como se desprende del análisis, la letra",
            "De la misma forma, la letra",
            "Adicionalmente, la letra",
            "Por su parte, la letra",
            "Además, la letra",
            "Luego, la letra",
        ]
        prefix = connectors[idx]
        contents = {
            "letter_b": f"""
                {prefix} b) establece una presunción de dolo o culpa grave en aquellos casos donde una de las operaciones 
                desconocidas por el usuario haya tenido como destino una cuenta de su misma titularidad, sin que sea 
                necesario que ambas pertenezcan a la misma institución bancaria.
            """,
            "letter_c": f"""
                {prefix} c) establece una presunción de dolo o culpa grave en aquellos casos donde se realiza un abono 
                justamente antes de la transacción que se busca desconocer.
            """,
            "letter_d": f"""
                {prefix} d) permite la presunción de dolo al momento en que el usuario admite haber entregado datos 
                personales, tal como ocurrío en este caso.
            """,
            "letter_g": f"""
                {prefix} g) establece una presunción de dolo o culpa grave cuando existan indicios de que el propio 
                usuario realizó la operación reclamada en canales físicos antes de solicitar restitución o cancelación 
                de cargos.
            """,
            "letter_h": f"""
                {prefix} h) establece una presunción de dolo o culpa grave si la operación se realizó con autenticación 
                reforzada en los términos del artículo 4, utilizando al menos un factor de inherencia. Sin perjuicio de 
                lo anterior, cuando solo se empleen factores de posesión o conocimiento, también podrá servir como base 
                de presunción judicial.
            """,
        }
        return contents.get(self.value, self.value)

    def get_body(self) -> str:
        contents = {
            "letter_b": """
                b) Que <b>la operación desconocida haya sido realizada exclusivamente entre cuentas de</b> 
                <span="bold-underline">su titularidad</span> y de su cónyuge o conviviente civil, o de 
                parientes por consanguinidad en toda la línea recta y la colateral hasta el cuarto grado 
                inclusive, o bien por afinidad en toda la línea recta y la colateral hasta el segundo 
                grado inclusive.
            """,
            "letter_c": """
                c) Que <b>los fondos transferidos hayan sido enviados a una o más cuentas registradas con 
                al menos cuarenta y ocho horas</b> de anticipación al desconocimiento de la operación por 
                el usuario, o se hubiere realizado transferencias a la o las cuentas de destino dos o más 
                veces antes de las cuarenta y ocho horas previas al desconocimiento de la operación.
            """,
            "letter_d": """
                d) Que <b>el usuario haya reconocido expresamente haber entregado sus claves 
                voluntariamente a terceros</b>, a sabiendas de que podrán ser usadas para giros o 
                transacciones.
            """,
            "letter_g": """
                g) Si el emisor tuviere <b>indicios suficientes de que fue el mismo usuario quien realizó 
                la operación reclamada en canales físicos</b> previo a la solicitud de restitución y/o 
                cancelación de cargos.
            """,
            "letter_h": """
                h) Si <b>la operación desconocida hubiere sido realizada con autenticación reforzada, en 
                los términos del artículo 4 de esta ley, siendo al menos uno de los factores de 
                autenticación de inherencia.</b> Sin perjuicio de lo anterior, si <b>la operación 
                desconocida hubiere sido realizada con autenticación reforzada, en los términos del 
                referido artículo, considerando sólo factores de posesión o conocimiento,</b> podrá servir 
                como base de presunción judicial.
            """,
        }
        return contents.get(self.value, self.value)
    
    def get_long_line(self, standalone: bool = False, context: dict | None = None) -> str:
        contents = {
            "letter_b": f"""
                {"Con respecto a lo anterior" if standalone else "En cuanto a la letra b),"} ya se pudo demostrar que la 
                transferencia realizada por ${context.get("amount")}, con fecha {context.get("date")} a las 
                {context.get("hour")} horas, fue realizada a una cuenta de la misma titularidad del usuario, 
                en {context.get("bank")}, lo que es suficiente para la configuración de dicha presunción.
            """ if context else f"""
                {"Con respecto a lo anterior" if standalone else "En cuanto a la letra b),"} ya se pudo demostrar que
                una transferencia fue realizada a una cuenta de la misma titularidad del usuario, 
                lo que es suficiente para la configuración de dicha presunción.
            """,
            "letter_c": f"""
                {"Considerando" if standalone else "En cuanto a la letra c), al considerar"} que
                en el presente caso la operación se efectuó después de un abono por la suma de ${context.get("amount")},
                es preciso señalar que los antecedentes presentados a S.S. constituyen un indicio suficiente para concluir 
                que fue el propio usuario quien realizó dichas transacciones.
            """ if context else f"""
                {"Lo anterior considerando" if standalone else "En cuanto a la letra c), se ha de considerar"} que
                en el presente caso la operación se efectuó después de un abono, 
                es preciso señalar que los antecedentes presentados a S.S. constituyen un indicio suficiente para concluir 
                que fue el propio usuario quien realizó dichas transacciones.
            """,
            "letter_d": f"""
                {"Lo anterior" if standalone else "En cuanto a la letra d),"} se verifica conforme a los 
                argumentos ya expuestos en el capítulo III <i>supra</i>. En específico, debido a que el usuario
                admitió haber compartido voluntariamente datos personales con terceros
                {f" (en este caso, a {context.get('person')})." if context else "."} Dicha conducta fue a sabiendas 
                que el tercero pudo haberlos utilizado para efectuar transacciones sin su consentimiento, esto 
                considerando que COOPEUCH reitera de manera constante a sus usuarios, a través de diversos medios, 
                la prohibición absoluta de compartir sus claves personales bajo cualquier supuesto, a fin de evitar 
                giros, avances o compras no autorizadas que podrían derivarse de dicho acto.
            """,
            "letter_g": f"""
                {"En lo anterior" if standalone else "En cuanto a la letra g),"} resulta relevante destacar que, en 
                el presente caso, la operación reclamada se efectuó mediante canales físicos.
                {f"En concreto, {context.get('argument')}." if context else ""} Por tanto, es preciso señalar que los 
                antecedentes presentados ante S.S. constituyen un indicio suficiente para concluir que fue el propio 
                usuario quien, de manera presencial y física, realizó la transacción.
            """,
            "letter_h": f"""
                {"Lo anterior" if standalone else "En cuanto a la letra h),"} es de suma importancia reiterarlo, 
                ya que, la sola existencia del sistema de autentificación forzada, lo que se cumple en este caso 
                conforme a los antecedentes hasta aquí presentados, tiene como consecuencia que S.S. debe acoger 
                esta solicitud.
            """,
        }
        return contents.get(self.value, self.value)
    
    def get_short_line(self) -> str:
        contents = {
            "letter_b": """
                una de las operaciones desconocidas se realizó a una cuenta de la misma titularidad del usuario
            """,
            "letter_c": """
                una de las operaciones desconocidas se realizó a una cuenta conocida con anticipación
            """,
            "letter_d": """
                el usuario compartió voluntariamente sus claves a terceros
            """,
            "letter_g": """
                transacciones realizadas ante canales físicos
            """,
            "letter_h": """
                existió autentificación forzada de conocimiento y de posesión
            """,
        }
        return contents.get(self.value, self.value)

    def to_spanish(self) -> str:
        translations = {
            "letter_b": "b)",
            "letter_c": "c)",
            "letter_d": "d)",
            "letter_g": "g)",
            "letter_h": "h)",
        }
        return translations.get(self.value, self.value)


class Gender(str, Enum):
    """Claimant partner gender."""
    FEMALE = "female"
    MALE = "male"


class SecuritySystem(str, Enum):
    """Security system."""
    MASTERCARD_CONNECT = "mastercard_connect"
    CELMEDIA = "celmedia"
    SAFESIGNER = "safesigner"

    def to_spanish(self) -> str:
        translations = {
            "mastercard_connect": "Mastercard Connect",
            "celmedia": "CELMEDIA",
            "safesigner": "SafeSigner",
        }
        return translations.get(self.value, self.value)


class TransactionType(str, Enum):
    """Transaction type."""
    NON_FACE_TO_FACE_PURCHASE = "non_face_to_face_purchase"
    BANK_TRANSFER = "bank_transfer"
    ATM_WITHDRAWAL = "atm_withdrawal"
    IN_PERSON_PURCHASE = "in_person_purchase"

    def to_spanish(self, plural=False) -> str:
        translations = {
            "non_face_to_face_purchase": ("una compra no presencial", "compras no presenciales"),
            "bank_transfer": ("una transferencia realizada vía internet", "transferencias realizadas vía internet"),
            "atm_withdrawal": ("un retiro en cajero", "retiros en cajero"),
            "in_person_purchase": ("una compra presencial", "compras presenciales"),
        }
        singular, plural_form = translations.get(self.value, (self.value, self.value))
        return plural_form if plural else singular


class Transaction(BaseModel):
    """Claimed transaction."""
    amount: float | None = Field(None, description="Transaction amount as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type, either 'clp', 'usd', or 'uf'")
    transaction_type: TransactionType | None = Field(None, description="Transaction type")
    transaction_datetime: datetime | None = Field(None, description="Transaction datetime")


class Payment(BaseModel):
    """Monetary payment instance."""
    amount: float | None = Field(None, description="Payment amount as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type, either 'clp', 'usd', or 'uf'")
    subsequent_balance: float | None = Field(None, description="Subsequent balance after payment as number")
    payment_datetime: datetime | None = Field(None, description="Payment datetime")


class SecurityMeasure(BaseModel):
    """Security measure."""
    security_system: SecuritySystem | None = Field(None, description="Security system used")
    context: str | None = Field(None, description="Written context related to security system use, in es_ES")
    transaction_amount: float | None = Field(None, description="Transaction amount where security system was used, if any, as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type, either 'clp', 'usd', or 'uf'")
    transaction_date: date | None = Field(None, description="Transaction date where security system was used")


class ClaimantPartner(BaseModel):
    """Claimant partner information."""
    name: str | None = Field(None, description="Partner name")
    rut: str | None = Field(None, description="Partner RUT identifier, in XX.XXX.XXX-X or X.XXX.XXX-X format, for example: 1.234.567-k")
    eibs_address: str | None = Field(None, description="Partner E-IBS address")
    affidavit_address: str | None = Field(None, description="Partner affidavit address")
    complaint_address: str | None = Field(None, description="Partner complaint address")
    eibs_phone_number: str | None = Field(None, description="Partner E-IBS phone number, in +XXX XXXXXXXX format, for example: +123 45678900")
    affidavit_phone_number: str | None = Field(None, description="Partner affidavit phone number, in +XXX XXXXXXXX format, for example: +123 45678900")
    complaint_phone_number: str | None = Field(None, description="Partner complaint phone number, in +XXX XXXXXXXX format, for example: +123 45678900")
    eibs_email: str | None = Field(None, description="Partner E-IBS e-mail")
    affidavit_email: str | None = Field(None, description="Partner affidavit e-mail")
    complaint_email: str | None = Field(None, description="Partner complaint e-mail")
    crm_complaint: str | None = Field(None, description="Partner CRM complaint code, for example CAS-123456-A1B2C3")
    has_more_complaints_due_ignorance_crm: bool | None = Field(None, description="True if partner has more complaints due to ignorance, False if NO")
    gender: Gender | None = Field(Gender.MALE, description="Partner gender deduced from their first name, either 'male' or 'female'")


class ClaimantRequest(BaseModel):
    """Claimant request information."""
    first_bank_account_box_interaction_date: date | None = Field(None, description="Date of first interaction with bank account box, also known as 1era Interacción con Casilla")
    affidavit_send_date: date | None = Field(None, description="Date when affidavit was send, also known as Envío de Declaración Jurada date")
    complaint_send_date: date | None = Field(None, description="Date when complaint was send, also known as Envío de Denuncia Policial date, either complete or incomplete")
    security_measures: list[SecurityMeasure] | None = Field([], description="Security measures that were in place")
    article_5_presumptions: list[Article5Presumption] | None = Field([], description="Letter 'b)', 'c)', 'd)', 'g)' or 'h)' presumptions related to article 5 that appear in the text")
    payments: list[Payment] | None = Field([], description="Payments that took place before or during transaction, if any")
    complaint_datetime: datetime | None = Field(None, description="Datetime when complaint was made to an office or police")
    valid_complaint_format: bool | None = Field(None, description="True if the claimant's complaint meets the legal requirements and is deemed as using a valid format")
    cca_report_exists: bool | None = Field(None, description="True if there is a explicit mention to a CCA report in the text")
    lost_phone_date: date | None = Field(None, description="Reported date of claimant's phone being lost or stolen, if any")
    lost_payment_card_date: date | None = Field(None, description="Reported date of claimant's payment card being lost or stolen, if any")


class CoopeuchReportInformation(InformationBaseModel):
    """COOPEUCH report information."""
    city: str | None = Field(None, description="City where the complaint was made")
    total_transaction_amount: float | None = Field(None, description="Total monetary amount of all claimed transactions, as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type of the total amount, either 'clp', 'usd', or 'uf'")
    claimed_transactions: list[Transaction] | None = Field([], description="Claimed transactions")
    claimant_partner: ClaimantPartner | None = Field(None, description="Claimant partner information")
    claimant_request: ClaimantRequest | None = Field(None, description="Claimant request information")


class CoopeuchReportExtractorInput(ExtractorInputBaseModel):
    """COOPEUCH report extractor input."""


class CoopeuchReportExtractorOutput(OutputBaseModel[CoopeuchReportInformation]):
    """COOPEUCH report extractor output."""
