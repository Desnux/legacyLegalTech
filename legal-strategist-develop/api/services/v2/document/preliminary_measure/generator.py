import logging
import os
import time as time_module
from collections import Counter
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader
from num2words import num2words
from weasyprint import HTML

from models.pydantic import CurrencyType, Locale
from services.v2.document.base import BaseGenerator, Metrics
from services.v2.document.coopeuch_report import (
    Article5Presumption,
    Payment,
    Gender,
    SecuritySystem,
    Transaction,
    TransactionType,
)
from util.generator import int_to_ordinal
from .models import (
    PreliminaryMeasureGeneratorInput,
    PreliminaryMeasureGeneratorOutput,
)


SPANISH_MONTHS = {
    1: "enero",   2: "febrero", 3: "marzo",     4: "abril",
    5: "mayo",    6: "junio",   7: "julio",     8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def find_latest_payment_before_transaction(transaction: Transaction, payments: list[Payment]) -> Payment | None:
    previous_payments = [
        p for p in payments
        if p.payment_datetime and transaction.transaction_datetime and p.payment_datetime < transaction.transaction_datetime
    ]
    if previous_payments:
        return max(previous_payments, key=lambda p: p.payment_datetime)
    return None


def format_amount(amount: Decimal | float | int, currency_type: CurrencyType | None = None) -> str:
    if not currency_type:
        currency_type = CurrencyType.CLP
    integer_part, fraction_part = f"{Decimal(amount):,.2f}".split(".")
    fraction_part = fraction_part.rstrip("0")
    integer_part = integer_part.replace(",", ".")
    if fraction_part:
        number_text = f"{integer_part},{fraction_part}"
    else:
        number_text = integer_part
    if currency_type == CurrencyType.USD:
        return f"{number_text} USD"
    if currency_type == CurrencyType.UF:
        return f"{number_text} UF"
    return f"${number_text}"


def format_date(dt: date) -> str:
    return f"{dt.day} de {SPANISH_MONTHS[dt.month]} de {dt.year}"


def format_datetime(dt: datetime) -> str:
    return f"{dt.day} de {SPANISH_MONTHS[dt.month]} de {dt.year}"


def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def format_unknown_dates(dates: list[datetime]) -> str:
    valid = sorted(d for d in dates if d is not None)
    if not valid:
        return ""
    if len(valid) == 1:
        return f"el día {format_datetime(valid[0])}"
    unique_days = {d.date() for d in valid}
    if len(unique_days) == 1:
        return f"el día {format_datetime(valid[0])}"
    days = sorted({d.day for d in valid})
    months = {d.month for d in valid}
    years = {d.year for d in valid}
    days_str = join_with_commas_and_y([str(d) for d in days])
    if len(months) == 1 and len(years) == 1:
        m = months.pop()
        y = years.pop()
        return f"los días {days_str} de {SPANISH_MONTHS[m]} de {y}"
    if len(years) == 1:
        y = years.pop()
        day_month_parts = [
            f"{d.day} de {SPANISH_MONTHS[d.month]}"
            for d in valid
        ]
        joined = join_with_commas_and_y(day_month_parts)
        return f"los días {joined} de {y}"
    full_parts = [
        f"{d.day} de {SPANISH_MONTHS[d.month]} de {d.year}"
        for d in valid
    ]
    joined = join_with_commas_and_y(full_parts)
    return f"los días {joined}"


def join_with_commas_and_y(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} y {items[1]}"
    return ", ".join(items[:-1]) + " y " + items[-1]


def num_to_words(value, default=""):
    try:
        n = int(value)
        if n == 1:
            return "un"
        return num2words(n, lang="es")
    except (ValueError, TypeError):
        return default


templates_dir = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader(templates_dir))
env.filters["num_to_words"] = num_to_words


class PreliminaryMeasureGenerator(BaseGenerator):
    """Preliminary measure generator."""

    def __init__(self, input: PreliminaryMeasureGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.presumptions = self._get_presumptions()
        self.security_systems = self._get_security_systems()
        self.transaction_type = self._get_transaction_type()
        self.multiple_transactions = False
    
    def generate(self) -> PreliminaryMeasureGeneratorOutput:
        """Generate preliminary measure structure from input."""
        metrics = Metrics(label="PreliminaryMeasureGenerator.generate")
        start_time = time_module.time()

        if not self.input.claimant_partner:
            raise ValueError("Missing claimant partner")
        if not self.input.claimant_partner.rut:
            raise ValueError("Missing claimant partner rut")
        if not self.input.claimant_partner.crm_complaint:
            raise ValueError("Missing claimant CRM code")
        if not self.input.claimant_partner.gender:
            logging.warning("Missing claimant partner gender")
            self.input.claimant_partner.gender = Gender.MALE

        if not self.input.claimant_request:
            raise ValueError("Missing claimant request")
        if not self.input.claimant_request.complaint_datetime:
            raise ValueError("Missing claimant request complaint datetime")
        complaint_datetime = self.input.claimant_request.complaint_datetime
        complaint_send_date = self.input.claimant_request.complaint_send_date
        valid_complaint_format = bool(self.input.claimant_request.valid_complaint_format)
        complaint_date = format_datetime(complaint_datetime)
        security_systems = [
            x.security_system.to_spanish() 
            for x in self.input.claimant_request.security_measures or []
            if x.security_system
        ]

        if not self.input.claimed_transactions:
            raise ValueError("Missing information about transactions")
        number_of_transactions = len(self.input.claimed_transactions)
        self.multiple_transactions = number_of_transactions > 1
        transaction_datetimes = sorted(d.transaction_datetime for d in self.input.claimed_transactions if d.transaction_datetime is not None)
        unknown_transaction_datetime = transaction_datetimes[0] if len(transaction_datetimes) > 0 else None
        if not self.input.total_transaction_amount:
            raise ValueError("Missing transaction amount")
        if self.input.total_transaction_amount < 1:
            raise ValueError("Invalid transaction amount")
        
        coopeuch_registry_uri = None
        transaction_to_self_uri = None
        payment_to_account_uri = None
        user_report_uri = None
        safesigner_report_uri = None
        mastercard_connect_report_uri = None
        celmedia_report_uri = None
        if not self.input.measure_information:
            raise ValueError("Missing specific preliminary measure information")
        if not self.input.measure_information.communication_date:
            raise ValueError("Missing comunication date")
        if uri := self.input.measure_information.coopeuch_registry_uri:
            coopeuch_registry_uri = uri
        if uri := self.input.measure_information.transaction_to_self_uri:
           transaction_to_self_uri = uri
        if uri := self.input.measure_information.payment_to_account_uri:
            payment_to_account_uri = uri
        if uri := self.input.measure_information.user_report_uri:
            user_report_uri = uri
        if uri := self.input.measure_information.safesigner_report_uri:
            safesigner_report_uri = uri
        if uri := self.input.measure_information.mastercard_connect_report_uri:
            mastercard_connect_report_uri = uri
        if uri := self.input.measure_information.celmedia_report_uri:
            celmedia_report_uri = uri
        title = "S.J. DE POLICÍA LOCAL"
        if city := self.input.city:
            title += f" DE {city.upper().strip()}"
        if local_police_number := self.input.measure_information.local_police_number:
            if local_police_number > 0:
                title += f" ({local_police_number}°)"
        communication_date = format_date(self.input.measure_information.communication_date)

        tx_datetimes = [tr.transaction_datetime for tr in self.input.claimed_transactions or []]
        first_presumption = self.presumptions[0].to_spanish() if len(self.presumptions) > 0 else None

        template = env.get_template("template.html")
        html_content = template.render(
            **self.input.model_dump(exclude={"total_transaction_amount"}),
            Gender=Gender,
            total_transaction_amount=format_amount(self.input.total_transaction_amount, self.input.currency_type),
            chapter_ii_date_range=self._summarize_date_range(tx_datetimes),
            chapter_ii_invalid_requirements=self._get_chapter_ii_invalid_requirements(
                self.input.claimant_partner.gender,
                complaint_send_date,
                complaint_datetime,
                unknown_transaction_datetime,
            ),
            chapter_ii_transactions=self._describe_transactions(self.input.claimed_transactions or []),
            chapter_ii_transactions_conclusion=self._get_chapter_ii_transactions_conclusion(self.input.claimed_transactions or []),
            chapter_ii_paragraphs=self._get_chapter_ii_paragraphs(
                self.input.claimant_partner.gender,
                self.input.claimed_transactions or [],
                transaction_to_self_uri,
                payment_to_account_uri,
            ),
            chapter_ii_severe_fault=self._get_chapter_ii_severe_fault(
                self.input.claimant_partner.gender,
                transaction_datetimes,
            ),
            valid_complaint_format=valid_complaint_format,
            chapter_iii_paragraphs=self._get_chapter_iii_paragraphs(),
            chapter_iv_paragraphs=self._get_chapter_iv_paragraphs(),
            chapter_vi_paragraphs=self._get_chapter_vi_paragraphs(),
            complaint_date=complaint_date,
            communication_date=communication_date,
            transaction_type=self.transaction_type.to_spanish(number_of_transactions > 1),
            first_presumption=first_presumption,
            number_of_transactions=number_of_transactions,
            security_systems=security_systems,
            security_measure_paragraphs=self._get_security_measure_paragraphs(),
            title=title,
            coopeuch_registry_uri=coopeuch_registry_uri,
            transaction_to_self_uri=transaction_to_self_uri,
            payment_to_account_uri=payment_to_account_uri,
            user_report_uri=user_report_uri,
            safesigner_report_uri=safesigner_report_uri,
            mastercard_connect_report_uri=mastercard_connect_report_uri,
            celmedia_report_uri=celmedia_report_uri,
        )

        logging.disable(logging.INFO)
        pdf_bytes = HTML(string=html_content).write_pdf()
        logging.disable(logging.NOTSET)

        metrics.time = round(time_module.time() - start_time, 4)
        return PreliminaryMeasureGeneratorOutput(metrics=metrics, pdf_bytes=pdf_bytes)

    def _describe_transactions(self, txs: list[Transaction]) -> list[str]:
        descriptions: list[str] = []

        for idx, tx in enumerate(txs, start=1):
            ord_word = int_to_ordinal(idx, Locale.ES_ES, True).lower()
            date_part: str | None = None
            amount_part: str | None = None
            if tx.transaction_datetime:
                d = tx.transaction_datetime
                date_part = (
                    f"Con fecha {format_datetime(d)}, "
                    f"alrededor de las {format_time(d)}, "
                )
            else:
                date_part = "En un tiempo indeterminado, "
            if tx.amount is not None:
                amount_part = f"por el monto de {format_amount(tx.amount, tx.currency_type)}"
            else:
                amount_part = None
            if date_part and amount_part:
                sentence = (
                    f"{date_part}se realizó la {ord_word} transacción {amount_part}."
                )
            elif date_part:
                sentence = f"{date_part}se realizó la {ord_word} transacción."
            elif amount_part:
                sentence = f"Se realizó la {ord_word} transacción {amount_part}."
            else:
                sentence = f"En un tiempo indeterminado, se realizó la {ord_word} transacción."
            if idx == 1:
                inner = sentence[0].lower() + sentence[1:]
                sentence = f"La cronología de las transacciones establece que {inner}"
            descriptions.append(sentence)
        return descriptions

    def _get_chapter_ii_invalid_requirements(
            self,
            gender: Gender,
            complaint_send_date: date | None,
            complaint: datetime,
            unknown_transaction: datetime | None,
            ) -> list[dict]:
        paragraphs = []
        if complaint_send_date:
            send_dt = datetime.combine(complaint_send_date, time.min)
        else:
            send_dt = None
        if unknown_transaction is None or (send_dt and send_dt < unknown_transaction + timedelta(hours=24)):
            return paragraphs
        user_name = "la usuaria" if gender == Gender.FEMALE else "el usuario"
        transaction_text = "las transacciones reclamadas" if self.multiple_transactions else "la transacción reclamada"
        acknowledgement_text = "mismo día en que estas fueron realizadas" if complaint.date() == unknown_transaction.date() else format_datetime(complaint)
        paragraphs.append({
            "body": f"""
                El relato {"de la usuaria" if gender == Gender.FEMALE else "del usuario"} ante 
                Carabineros, permite corroborar que {user_name} tomó conocimiento de 
                {transaction_text} el {acknowledgement_text}
            """.strip(),
        })
        if send_dt:
            delta = complaint_send_date - complaint.date()
            days_diff = delta.days + (1 if complaint.time() != datetime.min.time() else 0)
            last_paragraph = f"""
                Sin perjuicio de ello, y tal como se desprende del informe COOPEUCH, {user_name} 
                realizó su primer contacto con el emisor el {format_datetime(send_dt)}, <b>{days_diff} días</b> 
                después de haber tenido conocimiento del supuesto fraude. Este retraso excede lo que podría 
                considerarse un plazo razonable, incumpliendo los requisitos legales establecidos para que 
                el usuario limite su responsabilidad.
            """
        else:
            last_paragraph = f"""
                Sin perjuicio de ello, y tal como se desprende del informe COOPEUCH, {user_name} 
                no realiza envío de denuncia al emisor después de haber tenido conocimiento del supuesto fraude, 
                incumpliendo los requisitos legales establecidos para que el usuario limite su responsabilidad.
            """
        paragraphs.append({"body": last_paragraph.strip()})
        return paragraphs

    def _get_chapter_ii_paragraphs(
            self, 
            gender: Gender, 
            txs: list[Transaction], 
            transaction_to_self_uri: str | None,
            payment_to_account_uri: str | None
            ) -> list[dict]:
        paragraphs = []
        context = {} #TODO: Add context
        if transactions := self.input.claimed_transactions:
            paragraphs.append({"body": self._summarize_transactions(transactions)})
        else:
            paragraphs.append({"body": "varias transacciones" if self.multiple_transactions else "una transacción" })
        cca_report_exists = False
        payments = []
        if request := self.input.claimant_request:
            cca_report_exists = request.cca_report_exists
            payments = request.payments or []
        paragraphs.append({"body": "<br><br>".join([p.get_body().strip() for p in self.presumptions])})
        paragraphs.append({"body": " ".join([p.get_analysis_description(idx, context).strip() for idx, p in enumerate(self.presumptions)])})
        idx = 0
        connectors = [
            "En el presente caso,",
            "De la misma forma,",
            "Asimismo,",
            "Por otro lado,",
            "Adicionalmente,",
            "Finalmente,"
        ]
        if Article5Presumption.LETTER_B in self.presumptions:
            text = """
                En el presente caso, se observa que una de las operaciones desconocidas por la 
                contraparte corresponde efectivamente a una transferencia realizada hacia una 
                cuenta de su misma titularidad
            """.strip()
            if cca_report_exists:
                text += ", según lo corroborado mediante el informe emitido por la plataforma <u>externa</u> CCA. "
            else:
                text += ", según lo corroborado mediante el informe emitido por COOPEUCH. "
            if transaction_to_self_uri:
                text += f"""
                    Dicho documento permite verificar los siguientes datos:
                    <br><br>
                    <img
                        src="{transaction_to_self_uri}"
                        alt="Extracto de transacciones"
                        style="max-width:13.00cm; height:auto; border:1px solid #ccc; padding:4px;"
                    />
                """.strip()
            paragraphs.append({"body": text.strip()})
            user_name = "de la propia usuaria" if gender == Gender.FEMALE else "del propio usuario"
            paragraphs.append({
                "body": f"""
                    Por lo tanto, de acuerdo con los antecedentes presentados ante este tribunal, es 
                    posible afirmar con certeza que una de las operaciones desconocidas fue realizada 
                    hacia una cuenta de titularidad de {user_name} reclamante. Esto encuadra 
                    plenamente en la hipótesis prevista por la letra b) del artículo 5 ter de la Ley 
                    N° 20.009.
                """,
            })
            idx += 1

        if Article5Presumption.LETTER_C in self.presumptions:
            prefix = connectors[idx] if idx < len(connectors) else "Además,"
            text = f"{prefix} se observa que"
            payment = None
            transaction_idx = -1
            if payments:
                for i, tx in enumerate(transactions, 1):
                    payment = find_latest_payment_before_transaction(tx, payments)
                    if payment:
                        transaction_idx = i
                        break
            if payment:
                if self.multiple_transactions:
                    text += f" antes de la {int_to_ordinal(transaction_idx, Locale.ES_ES, True).lower()} de las transacciones"
                else:
                    text += " antes de la transacción"
                if amount := payment.amount:
                    text += f" se realiza un abono por el monto de {format_amount(amount, payment.currency_type)}. "
                else:
                    text += " se realiza un abono. "
            else:
                transaction_text = "de las transacciones que se buscan" if self.multiple_transactions else "de la transacción que se busca"
                text += f" se realiza un abono antes {transaction_text} desconocer. "
            if payment_to_account_uri:
                text += f"""
                    Esto puede verificarse mediante el informe de COOPEUCH:
                    <br><br>
                    <img
                        src="{payment_to_account_uri}"
                        alt="Extracto de abonos"
                        style="max-width:13.00cm; height:auto; border:1px solid #ccc; padding:4px;"
                    />
                """.strip()
            paragraphs.append({"body": text.strip()})
            idx += 1
        
        if Article5Presumption.LETTER_D in self.presumptions:
            prefix = connectors[idx] if idx < len(connectors) else "Además,"
            user_name = "la usuaria" if gender == Gender.FEMALE else "el usuario"
            text = f"""
                {prefix} {user_name} entregó datos personales a un tercero. De esta forma, 
                {user_name} facilitó la transacción. En la denuncia realizada ante Carabineros de 
                Chile, {user_name} establece haber entregado adatos personales para autorizar las 
                transferencias que posteriormente desconoce.
            """
            paragraphs.append({"body": text.strip()})
            idx += 1
    
        if Article5Presumption.LETTER_G in self.presumptions:
            prefix = connectors[idx] if idx < len(connectors) else "Además,"
            text = f"""
                {prefix} existen indicios suficientes para sostener que {user_name} realizó 
                personalmente la operación reclamada en un canal físico antes de solicitar la 
                restitución o cancelación de cargos. Esta circunstancia permite configurar la 
                presunción de dolo o culpa grave establecida en la ley.
            """
            paragraphs.append({"body": text.strip()})
            idx += 1

        if Article5Presumption.LETTER_H in self.presumptions:
            prefix = connectors[idx] if idx < len(connectors) else "Además,"
            text = f"""
                {prefix} la operación desconocida fue realizada utilizando autenticación reforzada, 
                en los términos del artículo 4 de la ley, con al menos un factor de inherencia. 
                En consecuencia, se configura la presunción de dolo o culpa grave conforme a la 
                normativa aplicable.
            """
            paragraphs.append({"body": text.strip()})
            idx += 1
        
        if len(self.presumptions) > 0:
            paragraphs.append({
                "body": f"""
                    En virtud de lo anterior, se configura la presunción simplemente legal de dolo o 
                    culpa grave en los términos dispuestos en el artículo 5 ter letra 
                    {join_with_commas_and_y([p.to_spanish() for p in self.presumptions])} de la referida 
                    ley, lo que constituye un antecedente suficiente para que este tribunal acoja la 
                    medida prejudicial solicitada, conforme al artículo 5 bis de la Ley Nº 20.009.
                """,
             })
        return paragraphs

    def _get_chapter_ii_severe_fault(self, gender: Gender, txs_datetimes: list[datetime]) -> list[dict]:
        paragraphs = []
        if not self.input.claimant_request:
            return paragraphs
        user_name = "de la usuaria" if gender == Gender.FEMALE else "del usuario"
        lost_payment_card_date = self.input.claimant_request.lost_payment_card_date
        lost_phone_date = self.input.claimant_request.lost_phone_date
        cca_report_exists = bool(self.input.claimant_request.cca_report_exists)
        transaction_text = "las transacciones reclamadas" if self.multiple_transactions else "la transacción reclamada"
        if not lost_payment_card_date and not lost_phone_date:
            return paragraphs
        if cca_report_exists:
            first_text = "Como consta a partir del informe de la plataforma CCA (extractado <i>supra</i>)"
        else:
            first_text = "Como consta del informe COOPEUCH"
        if len(txs_datetimes) > 1:
            dates_fragment = format_unknown_dates(txs_datetimes)
            first_text += f", las transacciones desconocidas fueron realizadas {dates_fragment}"
        elif len(txs_datetimes) == 1:
            first_text += f", la transacción desconocida fue realizada el día {format_datetime(txs_datetimes[0])}"
        if lost_payment_card_date:
            after_lost = [dt for dt in txs_datetimes if dt.date() > lost_payment_card_date]
            if after_lost:
                first_after = after_lost[0]
                days_before = (first_after.date() - lost_payment_card_date).days
                if days_before == 1:
                    days_before = "un día antes"
                elif days_before > 1:
                    days_before = f"{days_before} días antes"
                else:
                    days_before = "el mismo día"
                position = txs_datetimes.index(first_after) + 1
                ordinal_tx = int_to_ordinal(position, Locale.ES_ES, True).lower()
                if self.multiple_transactions:
                    paragraphs.append({
                        "body": f"""
                            {first_text}, mientras que el extravío de la tarjeta de la 
                            contraria ocurrió el {format_date(lost_payment_card_date)}, es decir, 
                            {days_before} de la {ordinal_tx} transacción desconocida.
                        """
                    })
                else:
                    paragraphs.append({
                        "body": f"""
                            {first_text}, mientras que el extravío del celular de la 
                            contraria ocurrió el {format_date(lost_phone_date)}, es decir, 
                            {days_before} de la transacción desconocida.
                        """
                    })
            else:
                paragraphs.append({
                    "body": f"""
                        {first_text}, mientras que el extravío de la tarjeta de la contraria ocurrió el 
                        {format_date(lost_phone_date)}, es decir, días después de {transaction_text}.
                    """,
                })
            paragraphs.append({
                "body": f"""
                    La ausencia de medidas inmediatas de protección por parte {user_name} tras el 
                    supuesto extravío de su tarjeta genera serias dudas sobre la diligencia de sus 
                    acciones y la credibilidad de su relato. No contactar al emisor en forma 
                    inmediata para reportar un extravío y bloquear de inmediato su cuenta COOPEUCH 
                    contraviene lo que razonablemente se esperaría de una persona que actúa con 
                    prudencia y cuidado respecto de su propiedad bancaria.
                """,
            })
            paragraphs.append({
                "body": f"""
                    Según el relato {user_name}, el extravío de su tarjeta habría sido el factor 
                    desencadenante que permitió la realización del supuesto fraude.
                """,
            })
        elif lost_phone_date:
            after_lost = [dt for dt in txs_datetimes if dt.date() > lost_phone_date]
            if after_lost:
                first_after = after_lost[0]
                days_before = (first_after.date() - lost_phone_date).days
                if days_before == 1:
                    days_before = "un día antes"
                elif days_before > 1:
                    days_before = f"{days_before} días antes"
                else:
                    days_before = "el mismo día"
                position = txs_datetimes.index(first_after) + 1
                ordinal_tx = int_to_ordinal(position, Locale.ES_ES, True).lower()
                if self.multiple_transactions:
                    paragraphs.append({
                        "body": f"""
                            {first_text}, mientras que el extravío del celular de la 
                            contraria ocurrió el {format_date(lost_phone_date)}, es decir, 
                            {days_before} de la {ordinal_tx} transacción desconocida.
                        """
                    })
                else:
                    paragraphs.append({
                        "body": f"""
                            {first_text}, mientras que el extravío del celular de la 
                            contraria ocurrió el {format_date(lost_phone_date)}, es decir, 
                            {days_before} de la transacción desconocida.
                        """
                    })
            else:
                paragraphs.append({
                    "body": f"""
                        {first_text}, mientras que el extravío del celular de la contraria ocurrió el 
                        {format_date(lost_phone_date)}, es decir, días después de {transaction_text}.
                    """,
                })
            paragraphs.append({
                "body": f"""
                    La ausencia de medidas inmediatas de protección por parte {user_name} tras el 
                    supuesto extravío de su celular genera serias dudas sobre la diligencia de sus 
                    acciones y la credibilidad de su relato. No contactar al emisor en forma 
                    inmediata para reportar un extravío y bloquear de inmediato su cuenta COOPEUCH 
                    contraviene lo que razonablemente se esperaría de una persona que actúa con 
                    prudencia y cuidado respecto de su propiedad bancaria.
                """,
            })
            paragraphs.append({
                "body": f"""
                    Según el relato {user_name}, el extravío de su celular habría sido el factor 
                    desencadenante que permitió la realización del supuesto fraude.
                """,
            })
        return paragraphs

    def _get_chapter_ii_transactions_conclusion(self, txs: list[Transaction]) -> str:
        affidavit_phone_number = None
        affidavit_email = None
        complaint_phone_number = None
        complaint_email = None
        phone_stolen = False
        payment_card_stolen = False
        given_password = Article5Presumption.LETTER_D in self.presumptions
        gender = Gender.MALE
        if partner := self.input.claimant_partner:
            if phone := partner.affidavit_phone_number:
                affidavit_phone_number = phone
            if mail := partner.affidavit_email:
                affidavit_email = mail
            if phone := partner.complaint_phone_number:
                complaint_phone_number = phone
            if mail := partner.complaint_email:
                complaint_email = mail
            if gen := partner.gender:
                gender = gen
        user_name = "la usuaria" if gender == Gender.FEMALE else "el usuario"
        if request := self.input.claimant_request:
            phone_stolen = bool(request.lost_phone_date)
            payment_card_stolen = bool(request.lost_payment_card_date)
        text = "Pues bien, las transacciones se realizaron"
        valid = sorted(d.transaction_datetime for d in txs if d.transaction_datetime is not None)
        unique_days = {dt.date() for dt in valid}
        distinct_days_count = len(unique_days)
        if distinct_days_count > 1:
            text += f" en {num_to_words(distinct_days_count)} días distintos,"
        if distinct_days_count == 1:
            text += f" a lo largo de un día,"
        text += f" con notificaciones mediante SMS y correo electrónico"
        if affidavit_phone_number and affidavit_email and complaint_phone_number and complaint_email:
            text += f", ambos los mismos que se establecen como propios por {user_name} en la declaración jurada y la denuncia"
        elif affidavit_phone_number and affidavit_email:
            text += f", ambos los mismos que se establecen como propios por {user_name} en la declaración jurada"
        elif complaint_phone_number and complaint_email:
            text += f", ambos los mismos que se establecen como propios por {user_name} en la denuncia"
        elif affidavit_phone_number and complaint_phone_number:
            text += f", el primero que se establece como propio por {user_name} en la declaración jurada y la denuncia"
        elif affidavit_email and complaint_email:
            text += f", el último que se establece como propio por {user_name} en la declaración jurada y la denuncia"
        elif affidavit_email:
            text += f", el último que se establece como propio por {user_name} en la declaración jurada"
        elif complaint_email:
            text += f", el último que se establece como propio por {user_name} en la denuncia"
        elif affidavit_phone_number:
            text += f", el primero que se establece como propio por {user_name} en la declaración jurada"
        elif complaint_phone_number:
            text += f", el primero que se establece como propio por {user_name} en la denuncia"
        if not phone_stolen and not payment_card_stolen:
            text += f""". No hace sentido, entonces, cómo es posible que {user_name} no haya tenido conocimiento de transacciones 
            que requieren en primer lugar, del factor de posesión (que se ingresen los datos de la tarjeta de forma 
            manual), el factor de conocimiento (que se ingrese la clave de internet), además del tercer factor especial 
            (que se autoricen cada una de las transacciones mediante un SMS enviado al teléfono de {user_name}, el que 
            debe ingresarse a la aplicación PASS COOPEUCH), cuando la única persona que tenía accesso era ella misma. 
            Lo anterior fundamentado en que no declaró haber perdido su tarjeta o su teléfono. Lo que hace imposible 
            perfeccionar una operación con la tarjeta COOPEUCH.
            """
        elif not phone_stolen:
            text += f""". No hace sentido, entonces, cómo es posible que {user_name} no haya tenido conocimiento de transacciones 
            que requieren en primer lugar, del factor de posesión (que se ingresen los datos de la tarjeta de forma 
            manual), y el factor de conocimiento (que se ingrese la clave de internet), cuando la única persona que 
            tenía accesso era ella misma. Lo anterior fundamentado en que no declaró haber perdido su tarjeta. 
            Lo que hace imposible perfeccionar una operación con la tarjeta COOPEUCH.
            """
        elif not payment_card_stolen:
            text += f""". No hace sentido, entonces, cómo es posible que {user_name} no haya tenido conocimiento de transacciones 
            que requieren en primer lugar, del factor de conocimiento (que se ingrese la clave de internet), además 
            del tercer factor especial (que se autoricen cada una de las transacciones mediante un SMS enviado al 
            teléfono de {user_name}, el que debe ingresarse a la aplicación PASS COOPEUCH), cuando la única persona que 
            tenía accesso era ella misma. Lo anterior fundamentado en que no declaró haber perdido su teléfono. Lo que 
            hace imposible perfeccionar una operación con la tarjeta COOPEUCH.
            """
        elif not given_password:
            text += f""". No hace sentido, entonces, cómo es posible que {user_name} no haya tenido conocimiento de transacciones 
            que requieren del factor de conocimiento (que se ingrese la clave de internet), cuando la única persona que 
            tenía accesso era ella misma. Lo que hace imposible perfeccionar una operación con la tarjeta COOPEUCH.
            """
        else:
            text += f""". Solo hace sentido, entonces, que {user_name} no haya tenido conocimiento de transacciones 
            que requieren en primer lugar, del factor de posesión (que se ingresen los datos de la tarjeta de forma 
            manual), el factor de conocimiento (que se ingrese la clave de internet), además del tercer factor especial 
            (que se autoricen cada una de las transacciones mediante un SMS enviado al teléfono de {user_name}, el que 
            debe ingresarse a la aplicación PASS COOPEUCH), al haber actuado con dolo o, en subsidio, culpa grave, facilitando 
            el supuesto fraude reclamado. Prueba de ello es que la contraparte no fue diligente en el sentido de mantener 
            resguardadas tanto su tarjeta y clave secreta de internet. Que haya descuidado ambas a la vez revela dolo o, 
            en subsidio, culpa grave de su parte.
            """
        return text

    def _get_chapter_iii_paragraphs(self) -> list[dict]:
        paragraphs = []
        phone_number = None
        gender = Gender.MALE
        security_measures = []
        if partner := self.input.claimant_partner:
            if phone := partner.affidavit_phone_number:
                phone_number = phone
            if gen := partner.gender:
                gender = gen
        if request := self.input.claimant_request:
            if s_measures := request.security_measures:
                security_measures = s_measures

        if self.transaction_type in [TransactionType.NON_FACE_TO_FACE_PURCHASE, TransactionType.BANK_TRANSFER]:
            paragraphs.append({
                "body": """
                    Para realizar una operación online con la tarjeta de débito <b>COOPEUCH se requiere una 
                    autenticación reforzada</b>, es decir, factor de posesión en confluencia con factor de 
                    conocimiento, por lo que se cumple con el presupuesto fáctico del artículo en comento.
                """,
            })
            paragraphs.append({
                "body": """
                    <u>Primero</u>, se requiere el factor de posesión, el cual consiste en el correcto 
                    ingreso de la información contenida en la tarjeta del usuario, de manera manual. El 
                    ingreso de los datos correspondientes es verificable a través de las plataformas 
                    <u>externas</u> Mastercard Connect y CELMEDIA.
                """,
            })
            paragraphs.append({
                "body": """
                    <u>Segundo</u>, se requiere ingreso de clave de internet, cuyo ingreso en este caso es 
                    validado como aprobado, es decir, correcto, por la plataforma <u>externa</u> Safesigner.
                """,
            })
            if SecuritySystem.CELMEDIA in self.security_systems and SecuritySystem.SAFESIGNER in self.security_systems:
                if phone_number:
                    paragraphs.append({
                        "body": f"""
                            <u>Tercero</u>, se requirió un medio especial de seguridad, adicional a los factores 
                            de posesión y conocimiento ya repasados, el cual consiste en una autorización de manera 
                            personal mediante PASS COOPEUCH, con un código enviado al teléfono del usuario (SMS). 
                            Debe destacarse que en este caso, <b>el código ha sido enviado, de acuerdo a plataforma 
                            <u>externa</u> CELMEDIA, al número telefónico “{phone_number}”, mismo número que la 
                            contraparte <u>reconoce</u> como propio en su declaración jurada de desconocimiento de 
                            transacciones.</b> Esta es una prueba inequívoca e irrefutable de que las transacciones 
                            fueron autorizadas por la contraria, o bien que se realizaron por su propio dolo o 
                            culpa grave.
                        """,
                    })
                else:
                    paragraphs.append({
                        "body": """
                            <u>Tercero</u>, se requirió un medio especial de seguridad, adicional a los factores 
                            de posesión y conocimiento ya repasados, el cual consiste en una autorización de manera 
                            personal mediante PASS COOPEUCH, con un código enviado al teléfono del usuario (SMS).
                        """,
                    })
            elif SecuritySystem.SAFESIGNER in self.security_systems:
                paragraphs.append({
                    "body": """
                        <u>Tercero</u>, se requirió un medio especial de seguridad, adicional a los factores 
                        de posesión y conocimiento ya repasados, el cual consiste en el ingreso correcto de 
                        la información contenida en la aplicación <b>tarjeta de coordenadas del usuario</b>. Esta 
                        medida de seguridad es verificable a través de la plataforma <u>externa</u> Safesigner en 
                        cuanto a su correcta digitación.
                    """,
                })
            else:
                paragraphs.append({"body": ""})
        else:
            paragraphs.append({
                "body": """
                    Para realizar una operación presencial con la tarjeta de débito <b>COOPEUCH se requiere una 
                    autenticación reforzada</b>, es decir, factor de posesión en confluencia con factor de 
                    conocimiento, por lo que se cumple con el presupuesto fáctico del artículo en comento.
                """,
            })
            paragraphs.append({
                "body": """
                    <u>Primero</u>, se requiere el factor de posesión. Para las compras 
                    presenciales, este factor se configura mediante el contacto físico de la 
                    tarjeta con <i>chip</i> y el dispositivo de venta; mientras que, para los giros 
                    presenciales, se materializa mediante la inserción física de la tarjeta en 
                    el cajero automático. En el caso de las compras presenciales, el contacto 
                    entre la tarjeta y el dispositivo de venta puede verificarse a través de la 
                    plataforma <u>externa</u> <b>Mastercard Connect</b>. Por su parte, la inserción de 
                    la tarjeta en el cajero automático queda constatada mediante el estado 
                    de cuenta y el historial de transacciones del usuario, los cuales forman 
                    parte integrante del informe de COOPEUCH.
                """,
            })
            paragraphs.append({
                "body": """
                    <u>Segundo</u>, se requiere el factor de conocimiento: algo que el usuario
                    sabe. Para efectuar los movimientos descritos, es necesario ingresar la 
                    clave PIN, cuyo conocimiento es exclusivo del usuario. COOPEUCH 
                    reitera a sus clientes que nunca deben compartir ni entregar sus claves, 
                    como se detallará <i>infra</i>.
                """,
            })
            paragraphs.append({"body": ""})

        if SecuritySystem.SAFESIGNER in self.security_systems:
            paragraphs.append({"body": " las cuales son verificables a través de la plataforma <u>externa</u> Safesigner"})
        elif SecuritySystem.MASTERCARD_CONNECT in self.security_systems:
            paragraphs.append({"body": " las cuales son verificables a través de la plataforma <u>externa</u> Mastercard Connect"})
        else:
            paragraphs.append({"body": ""})

        if len(self.security_systems) == 1:
            paragraphs.append({"body": f"<b>la plataforma <u>externa</u> {self.security_systems[0].to_spanish()}</b>"})
        elif len(self.security_systems) > 1:
            order = [
                SecuritySystem.MASTERCARD_CONNECT,
                SecuritySystem.CELMEDIA,
                SecuritySystem.SAFESIGNER,
            ]
            names = [s.to_spanish() for s in order if s in self.security_systems]
            text =  ", ".join(names[:-1]) + " y " + names[-1]
            paragraphs.append({"body": f"<b>las plataformas <u>externas</u> {text}</b>"})
        else:
            paragraphs.append({"body": ""})

        if SecuritySystem.SAFESIGNER in self.security_systems:
            if SecuritySystem.MASTERCARD_CONNECT in self.security_systems and SecuritySystem.CELMEDIA in self.security_systems:
                paragraphs.append({
                    "body": """
                        En este caso en particular, se acompaña documento Safesigner que muestra 
                        como correctamente autorizadas (digitación correcta de clave de internet) 
                        las transacciones objetadas, y el informe de las plataformas Mastercard 
                        Connect y CELMEDIA, que dan cuenta de la correcta digitación manual de la 
                        información contenida en la tarjeta del usuario.
                    """,
                })
            elif SecuritySystem.MASTERCARD_CONNECT in self.security_systems:
                paragraphs.append({
                    "body": """
                        En este caso en particular, se acompaña documento Safesigner que muestra 
                        como correctamente autorizadas (digitación correcta de clave de internet) 
                        las transacciones objetadas, y el informe de la plataforma Mastercard
                        Connect, que da cuenta de la correcta digitación manual de la información 
                        contenida en la tarjeta del usuario.
                    """,
                })
            elif SecuritySystem.CELMEDIA in self.security_systems:
                paragraphs.append({
                    "body": """
                        En este caso en particular, se acompaña documento Safesigner que muestra 
                        como correctamente autorizadas (digitación correcta de clave de internet) 
                        las transacciones objetadas, y el informe de la plataforma CELMEDIA, que 
                        da cuenta de la correcta digitación manual de la información contenida 
                        en la tarjeta del usuario.
                    """,
                })
            else:
                paragraphs.append({
                    "body": """
                        En este caso en particular, se acompaña documento Safesigner que muestra 
                        como correctamente autorizadas (digitación correcta de clave de internet) 
                        las transacciones objetadas.
                    """,
                })
            paragraphs.append({
                "body": """
                    En cuanto a la clave de internet (factor de conocimiento), su correcto ingreso 
                    puede verificarse a través del informe de la plataforma externa Safesigner. 
                    Este documento fue clave en la investigación interna realizada por COOPEUCH 
                    para detectar este caso como uno en que la contraria incurrió en dolo o culpa 
                    grave, pues demuestra que las contraseñas se ingresaron de manera correcta y 
                    sin intentos erróneos.
                """,
            })

            safesigner_security_measure = next(
                (measure for measure in security_measures if measure.security_system == SecuritySystem.SAFESIGNER),
                None,
            )
            if safesigner_security_measure:
                transaction_amount = None
                transaction_date = None
                if t_date := safesigner_security_measure.transaction_date:
                    transaction_date = format_date(t_date)
                if t_amount := safesigner_security_measure.transaction_amount:
                    transaction_amount = format_amount(t_amount, safesigner_security_measure.currency_type)
                if transaction_amount and transaction_date:
                    paragraphs.append({
                        "body": f"""
                            Como puede apreciarse del extracto recién reproducido, para el cual se tomó como 
                            ejemplo la transacción por {transaction_amount}, realizada el {transaction_date}, 
                            la misma fue autorizada a través de clave de 
                            internet (“AUTH Validation”), Tarjeta de Coordenadas (“Challenge Operation”, 
                            “Card Challenge” y “Card Response”) y mensaje SMS (“SMS Challenge” y “SMS 
                            Response”), todos los cuales arrojan la glosa “SUCCESS”.
                        """,
                    })
                elif transaction_amount:
                    paragraphs.append({
                        "body": f"""
                            Como puede apreciarse del extracto recién reproducido, para el cual se tomó como 
                            ejemplo la transacción por {transaction_amount}, la misma fue autorizada a través de clave de 
                            internet (“AUTH Validation”), Tarjeta de Coordenadas (“Challenge Operation”, 
                            “Card Challenge” y “Card Response”) y mensaje SMS (“SMS Challenge” y “SMS 
                            Response”), todos los cuales arrojan la glosa “SUCCESS”.
                        """,
                    })
                elif transaction_date:
                    paragraphs.append({
                        "body": f"""
                            Como puede apreciarse del extracto recién reproducido, para el cual se tomó como 
                            ejemplo la transacción realizada el {transaction_date}, la misma fue autorizada a través de clave de 
                            internet (“AUTH Validation”), Tarjeta de Coordenadas (“Challenge Operation”, 
                            “Card Challenge” y “Card Response”) y mensaje SMS (“SMS Challenge” y “SMS 
                            Response”), todos los cuales arrojan la glosa “SUCCESS”.
                        """,
                    })
                else:
                    paragraphs.append({
                        "body": f"""
                            Como puede apreciarse del extracto recién reproducido, se autorizó una transacción a través de clave de 
                            internet (“AUTH Validation”), Tarjeta de Coordenadas (“Challenge Operation”, 
                            “Card Challenge” y “Card Response”) y mensaje SMS (“SMS Challenge” y “SMS 
                            Response”), todos los cuales arrojan la glosa “SUCCESS”.
                        """,
                    })
            else:
                paragraphs.append({"body": ""})
        else:
            paragraphs.append({"body": ""})
            paragraphs.append({"body": ""})
            paragraphs.append({"body": ""})

        if phone_number and SecuritySystem.CELMEDIA in self.security_systems:
            paragraphs.append({
                "body": f"""
                    De la misma forma, el informe de la plataforma externa CELMEDIA establece que 
                    la transacción fue efectivamente autorizada mediante PASS COOPEUCH, mediante 
                    el envío de una clave secreta y de uso personal al número de teléfono declarado 
                    como propio por { "la usuaria" if gender == Gender.FEMALE else "el usuario" } 
                    en la declaración jurada. Este se expone a continuación:
                """
            }),
        elif SecuritySystem.CELMEDIA in self.security_systems:
            paragraphs.append({
                "body": f"""
                    De la misma forma, el informe de la plataforma externa CELMEDIA establece que 
                    la transacción fue efectivamente autorizada mediante PASS COOPEUCH, mediante 
                    el envío de una clave secreta. Este se expone a continuación:
                """
            }),
        else:
            paragraphs.append({"body": ""})
        
        if len(self.security_systems) > 0:
            order = [
                SecuritySystem.MASTERCARD_CONNECT,
                SecuritySystem.CELMEDIA,
                SecuritySystem.SAFESIGNER,
            ]
            names = ", ".join([f"el de {s.to_spanish()}" for s in order if s in self.security_systems])
            paragraphs.append({
                "body": f"""
                    Este tribunal puede cotejar los distintos informes: {names} y el de COOPEUCH, notando que las transacciones 
                    en cuestión efectivamente aparecen como autorizadas, momento en el cual se 
                    verificó el último pasó para la operación, es decir, el ingreso del código enviado 
                    vía mensaje de texto al teléfono (reconocido como propio) de la contraria.
                """ if phone_number else """
                    Este tribunal puede cotejar los distintos informes: {names} y el de COOPEUCH, notando que las transacciones 
                    en cuestión efectivamente aparecen como autorizadas.
                """,
            })
        else:
            paragraphs.append({
                "body": """
                    Este tribunal puede cotejar el informe de COOPEUCH, notando que las transacciones 
                    en cuestión efectivamente aparecen como autorizadas, momento en el cual se 
                    verificó el último pasó para la operación, es decir, el ingreso del código enviado 
                    vía mensaje de texto al teléfono (reconocido como propio) de la contraria.
                """ if phone_number else """
                    Este tribunal puede cotejar el informe de COOPEUCH, notando que las transacciones 
                    en cuestión efectivamente aparecen como autorizadas.
                """,
            })
        return paragraphs

    def _get_chapter_iv_paragraphs(self) -> list[dict]:
        paragraphs = []
        context = {} #TODO: Add context
        if len(self.presumptions) > 0:
            if len(self.presumptions) == 1:
                paragraphs.append({"body": "una"})
                paragraphs.append({"body": f"la de la letra {self.presumptions[0].to_spanish()}"})
                paragraphs.append({"body": f"<u>{self.presumptions[0].get_short_line()}</u>"})
            else:
                first_half = self.presumptions[:-1]
                last_half = self.presumptions[-1]
                paragraphs.append({"body": num_to_words(len(self.presumptions))})
                paragraphs.append({"body": "las de las letra " + ", ".join([p.to_spanish() for p in first_half]) + f" y {last_half.to_spanish()}"})
                paragraphs.append({"body": ", ".join([f"<u>{p.get_short_line()}</u>" for p in first_half]) + f" y <u>{last_half.get_short_line()}</u>"})
            paragraphs.append({"body": "<br><br>".join([p.get_body().strip() for p in self.presumptions])})
            if len(self.presumptions) == 1:
                paragraphs.append({"body": self.presumptions[0].get_long_line(True, context)})
            else:
                for p in self.presumptions:
                    paragraphs.append({"body": p.get_long_line(False, context)})
        return paragraphs

    def _get_chapter_vi_paragraphs(self) -> list[dict]:
        paragraphs = []
        has_possession_factor = False
        has_knowledge_factor = False
        if (SecuritySystem.MASTERCARD_CONNECT in self.security_systems or SecuritySystem.CELMEDIA in self.security_systems):
            has_possession_factor = True
        if SecuritySystem.SAFESIGNER in self.security_systems:
            has_knowledge_factor = True
        if has_possession_factor and has_knowledge_factor:
            paragraphs.append({
                "body": """
                    Ha quedado establecido por sentencia firme y ejecutoriada de la Iltma. Corte de Apelaciones 
                    de Santiago que es responsabilidad del usuario el cuidado de sus datos de seguridad. 
                    Considerando que <b>en este caso</b> las transacciones desconocidas fueron realizadas mediante 
                    factor de seguridad de posesión (código enviado a la tarjeta de la contraparte) y factor 
                    de conocimiento (clave de internet), no es explicable que los movimientos se hayan 
                    realizado sin dolo o culpa grave de la contraparte.
                """,
            })
            paragraphs.append({
                "body": """
                    La sentencia anterior muestra un caso en que el usuario descuidó su factor de seguridad de 
                    posesión (algo que tenía: el digipass) y a su vez descuidó su factor de seguridad de 
                    conocimiento (algo que él sabía: contraseña). La solución de la Iltma. Corte de Apelaciones 
                    de Santiago fue establecer que el supuesto fraude se había verificado debido a la propia 
                    negligencia del usuario. <b>En el presente caso,</b> la contraparte también descuidó su factor de 
                    posesión y su factor de conocimiento. Corresponde, como es evidente, aplicar la misma solución.
                """,
            })
            paragraphs.append({
                "body": """
                    Así, inclusive descartándose el dolo en la actuación de la contraparte, debe atenderse a que, 
                    en subsidio, se alega culpa grave en la ocurrencia de los hechos, toda vez que se verificó el 
                    uso de su factor de posesión (tarjeta) y factor de conocimiento (clave de internet). Ambos 
                    factores son de carácter personal y, por lo tanto, de resguardo estricto por parte del usuario.
                """,
            })
            paragraphs.append({
                "body": """
                    En conclusión S.S., la contraria actuó con dolo o, en subsidio, culpa grave, facilitando 
                    el supuesto fraude reclamado. Prueba de ello es que la contraparte no fue diligente en el 
                    sentido de mantener resguardadas tanto su tarjeta y clave secreta de internet. Que haya 
                    descuidado ambas a la vez revela dolo o, en subsidio, culpa grave de su parte.
                """,
            })
        elif has_possession_factor:
            paragraphs.append({
                "body": """
                    Ha quedado establecido por sentencia firme y ejecutoriada de la Iltma. Corte de Apelaciones 
                    de Santiago que es responsabilidad del usuario el cuidado de sus datos de seguridad. 
                    Considerando que <b>en este caso</b> las transacciones desconocidas fueron realizadas mediante 
                    factor de seguridad de posesión (código enviado a la tarjeta de la contraparte), no es explicable 
                    que los movimientos se hayan realizado sin dolo o culpa grave de la contraparte.
                """,
            })
            paragraphs.append({
                "body": """
                    La sentencia anterior muestra un caso en que el usuario descuidó su factor de seguridad de 
                    posesión (algo que tenía: el digipass). La solución de la Iltma. Corte de Apelaciones 
                    de Santiago fue establecer que el supuesto fraude se había verificado debido a la propia 
                    negligencia del usuario. <b>En el presente caso,</b> la contraparte también descuidó su factor de 
                    posesión. Corresponde, como es evidente, aplicar la misma solución.
                """,
            })
            paragraphs.append({
                "body": """
                    Así, inclusive descartándose el dolo en la actuación de la contraparte, debe atenderse a que, 
                    en subsidio, se alega culpa grave en la ocurrencia de los hechos, toda vez que se verificó el 
                    uso de su factor de posesión (tarjeta). Factor de carácter personal y, por lo tanto, de resguardo 
                    estricto por parte del usuario.
                """,
            })
            paragraphs.append({
                "body": """
                    En conclusión S.S., la contraria actuó con dolo o, en subsidio, culpa grave, facilitando 
                    el supuesto fraude reclamado. Prueba de ello es que la contraparte no fue diligente en el 
                    sentido de mantener resguardada su tarjeta. Que haya descuidado su tarjeta 
                    revela dolo o, en subsidio, culpa grave de su parte.
                """,
            })
        elif has_knowledge_factor:
            paragraphs.append({
                "body": """
                    Ha quedado establecido por sentencia firme y ejecutoriada de la Iltma. Corte de Apelaciones 
                    de Santiago que es responsabilidad del usuario el cuidado de sus datos de seguridad. 
                    Considerando que <b>en este caso</b> las transacciones desconocidas fueron realizadas mediante 
                    factor de conocimiento (clave de internet), no es explicable que los movimientos se hayan 
                    realizado sin dolo o culpa grave de la contraparte.
                """,
            })
            paragraphs.append({
                "body": """
                    La sentencia anterior muestra un caso en que el usuario descuidó su factor de seguridad de 
                    conocimiento (algo que él sabía: contraseña). La solución de la Iltma. Corte de Apelaciones 
                    de Santiago fue establecer que el supuesto fraude se había verificado debido a la propia 
                    negligencia del usuario. <b>En el presente caso,</b> la contraparte también descuidó su factor de 
                    conocimiento. Corresponde, como es evidente, aplicar la misma solución.
                """,
            })
            paragraphs.append({
                "body": """
                    Así, inclusive descartándose el dolo en la actuación de la contraparte, debe atenderse a que, 
                    en subsidio, se alega culpa grave en la ocurrencia de los hechos, toda vez que se verificó el 
                    uso de su factor de conocimiento (clave de internet). Factor de carácter personal y, por lo 
                    tanto, de resguardo estricto por parte del usuario.
                """,
            })
            paragraphs.append({
                "body": """
                    En conclusión S.S., la contraria actuó con dolo o, en subsidio, culpa grave, facilitando 
                    el supuesto fraude reclamado. Prueba de ello es que la contraparte no fue diligente en el 
                    sentido de mantener resguardada su clave secreta de internet. Que haya descuidado su clave revela 
                    dolo o, en subsidio, culpa grave de su parte.
                """,
            })
        else:
            paragraphs.append({
                "body": """
                    Ha quedado establecido por sentencia firme y ejecutoriada de la Iltma. Corte de Apelaciones 
                    de Santiago que es responsabilidad del usuario el cuidado de sus datos de seguridad. 
                """,
            })
            paragraphs.append({
                "body": """
                    La sentencia anterior muestra un caso en que el usuario descuidó su factor de seguridad de 
                    posesión (algo que tenía: el digipass) y a su vez descuidó su factor de seguridad de 
                    conocimiento (algo que él sabía: contraseña). La solución de la Iltma. Corte de Apelaciones 
                    de Santiago fue establecer que el supuesto fraude se había verificado debido a la propia 
                    negligencia del usuario.
                """,
            })
            paragraphs.append({
                "body": """
                    Así, inclusive descartándose el dolo en la actuación de la contraparte, debe atenderse a que, 
                    en subsidio, se alega culpa grave en la ocurrencia de los hechos.
                """,
            })
            paragraphs.append({
                "body": """
                    En conclusión S.S., la contraria actuó con dolo o, en subsidio, culpa grave, facilitando 
                    el supuesto fraude reclamado.
                """,
            })
        return paragraphs

    def _get_presumptions(self) -> list[Article5Presumption]:
        if request := self.input.claimant_request:
            order = [
                Article5Presumption.LETTER_B,
                Article5Presumption.LETTER_C,
                Article5Presumption.LETTER_D,
                Article5Presumption.LETTER_G,
                Article5Presumption.LETTER_H,
            ]
            return [p for p in order if request.article_5_presumptions and p in request.article_5_presumptions]
        return []

    def _get_security_systems(self) -> list[SecuritySystem]:
        if request := self.input.claimant_request:
            return [x.security_system for x in request.security_measures or [] if x.security_system]
        return []

    def _get_security_measure_paragraphs(self) -> list[dict]:
        paragraphs = []
        # i. Possession factor
        if (SecuritySystem.MASTERCARD_CONNECT in self.security_systems or SecuritySystem.CELMEDIA in self.security_systems):
            fragment = "las plataformas externas Mastercard Connect y CELMEDIA, las cuales demuestran"
            if not SecuritySystem.MASTERCARD_CONNECT in self.security_systems:
                fragment = "las plataforma externa CELMEDIA, la cual demuestra"
            if not SecuritySystem.CELMEDIA in self.security_systems:
                fragment = "las plataforma externa Mastercard Connect, la cual demuestra"
            paragraphs.append({
                "title": "<span class='italic'>Factor de posesión (algo que el usuario tiene).</span>",
                "body": f"""
                    Las operaciones fueron autorizadas mediante el ingreso de información 
                    contenida en la tarjeta física exclusiva única y exclusivamente a la contraparte. 
                    Esto es verificable a través de informe de {fragment} que se ingresaron correctamente y de 
                    manera manual los datos de la tarjeta en cuestión, siendo estas autorizadas 
                    mediante el ingreso del código enviado por SMS al teléfono celular de la 
                    contraria.
                """,
            })
        # ii. Knowledge factor
        if SecuritySystem.SAFESIGNER in self.security_systems:
            paragraphs.append({
                "title": "<span class='italic'>Factor de conocimiento (algo que el usuario sabe).</span>",
                "body": """
                    La plataforma externa Safesigner muestra que las operaciones se realizaron con 
                    ingreso correcto de la clave de internet de la contraria, mostrando como 
                    resultado la glosa “SUCCESS”.
                """,
            })
        # iii. Special third factor
        if SecuritySystem.CELMEDIA in self.security_systems and SecuritySystem.SAFESIGNER in self.security_systems:
            paragraphs.append({
                "title": "<span class='italic'>Tercer factor especial:</span>",
                "body": """
                    autorización de la transacción mediante PASS COOPEUCH mediante un mensaje de 
                    texto (SMS) enviado oportunamente al teléfono que la usuaria registra como cuyo 
                    en la Declaración Jurada al realizar el reclamo. Esto es comprobable mediante el 
                    informe de CELMEDIA.
                """,
            })
        return paragraphs

    def _get_transaction_type(self) -> TransactionType:
        txs = self.input.claimed_transactions
        if not txs:
            return TransactionType.NON_FACE_TO_FACE_PURCHASE
        counts = Counter()
        for tx in txs:
            if tx.transaction_type is not None:
                counts[tx.transaction_type] += 1
        priority = { t: i for i, t in enumerate(TransactionType) }
        best = max(TransactionType, key=lambda t: (counts.get(t, 0), -priority[t]))
        return best

    def _summarize_date_range(self, dates: list[datetime | None]) -> str:
        valid = sorted(d for d in dates if d is not None)
        if len(valid) == 1:
            return "en torno al " + format_date(self.input.measure_information.communication_date)
        if len(valid) == 0:
            return "en las fechas indicadas"
        
        f, l = valid[0], valid[-1]
        d1, m1, y1 = f.day, f.month, f.year
        d2, m2, y2 = l.day, l.month, l.year

        mon1 = SPANISH_MONTHS[m1]
        mon2 = SPANISH_MONTHS[m2]

        if y1 == y2:
            if m1 == m2:
                if d1 == d2:
                    return f"el {d1} de {mon1} de {y1}"
                return f"entre el {d1} y {d2} de {mon1} de {y1}"
            return f"entre el {d1} de {mon1} y {d2} de {mon2} de {y1}"
        return f"entre el {d1} de {mon1} de {y1} y {d2} de {mon2} de {y2}"

    def _summarize_transactions(self, transactions: list[Transaction]) -> str:
        counts = Counter(
            tx.transaction_type
            for tx in transactions
            if tx.transaction_type is not None
        )
        chunks: list[str] = []
        for ttype in TransactionType:
            cnt = counts.get(ttype, 0)
            if cnt == 0:
                continue
            text = ttype.to_spanish(plural=(cnt > 1))
            chunk = f"{cnt} {text}" if cnt > 1 else text
            chunks.append(chunk)
        if not chunks:
            return ""
        if len(chunks) == 1:
            return chunks[0]
        if len(chunks) == 2:
            return f"{chunks[0]} y {chunks[1]}"
        return ", ".join(chunks[:-1]) + " y " + chunks[-1]
