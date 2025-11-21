import io
import pandas as pd
import zipfile
from sqlmodel import func, select, or_
from uuid import UUID

from database.ext_db import Session
from models.pydantic import LegalSubject, ProbableCaseStats
from models.sql import Case, CaseEvent, CaseEventType, CaseStats, CaseStatsEvent


BANK_FILTER = {
    "banco-bci": "inversio",
    "banco-bice": "bice",
    "banco-consorcio": "consorcio",
    "banco-de-chile": "chile",
    "banco-estado": "estado",
    "banco-itau": "itau",
    "banco-santander": "santander",
    "banco-security": "security",
    "scotiabank": "scotiabank",
}

BANK_TRANSLATION = {
    "banco-bci": "Banco BCI",
    "banco-bice": "Banco BICE",
    "banco-consorcio": "Banco Consorcio",
    "banco-de-chile": "Banco de Chile",
    "banco-estado": "Banco Estado",
    "banco-itau": "Banco Itaú",
    "banco-santander": "Banco Santander",
    "banco-security": "Banco Security",
    "scotiabank": "Scotiabank",
}

CASE_TYPE_TRANSLATIONS = {
    "dispossession": "Acción de desposeimiento",
    "invoice_collection": "Cobro de factura",
    "loan_collection": "Cobro ejecutivo de mutuo",
    "promissory_note_collection": "Cobro de pagaré",
}

LEGAL_STAGE_TRANSLATIONS = {
    "active": "Tramitación",
    "archived": "Archivada",
    "demand_notification": "Notificación demanda",
    "exceptions": "Excepciones",
    "exceptions_response": "Contestación excepciones",
    "finished": "Terminada",
    "legal_sentence": "Sentencia",
    "pending": "Pendiente",
    "sentence_appeal": "Impugnación de sentencia",
}

RESULT_TRANSLATIONS = {
    "accumulated": "Acumulada",
    "desisted": "Desistida",
    "pending": "Pendiente",
    "sentence_for_defendants": "Sentencia a favor de ejecutados",
    "sentence_for_plaintiffs": "Sentencia a favor de ejecutantes",
    "settlement": "Avenimiento",
    "suspended": "Suspendida",
}


def map_events_to_legal_stage(event_types: list[CaseEventType]) -> str:
    events_set = set(event_types)
    if CaseEventType.EXCEPTIONS_RESPONSE in events_set:
        return "exceptions_response"
    if CaseEventType.EXCEPTIONS in events_set:
        return "exceptions"
    if CaseEventType.DISPATCH_RESOLUTION in events_set:
        return "demand_notification"
    if CaseEventType.DEMAND_START in events_set:
        return "demand_notification"
    if CaseEventType.COMPROMISE in events_set:
        return "finished"
    return "active"


class Statistics:
    """Statistics handlers."""

    def get_case_count(self, session: Session, bank: str, status: list[str] | None) -> int:
        """Returns the amount of cases that satisfy the filters."""
        query = select(func.count(CaseStats.id))
        if bank:
            query = query.where(CaseStats.bank == bank)
            if title_filter := BANK_FILTER.get(bank):
                query = query.where(CaseStats.title.ilike(f"%{title_filter}%"))
        if status:
            conditions = []
            if "active" in status:
                conditions.append(~CaseStats.legal_stage.in_(["draft", "finished", "archived"]))
            other_statuses = [s for s in status if s != "active"]
            if other_statuses:
                conditions.append(CaseStats.legal_stage.in_(other_statuses))
            query = query.where(or_(*conditions))
        count = session.exec(query).first()
        return count or 0

    def get_case_events(self, session: Session, case_id: UUID) -> list[CaseStatsEvent]:
        """Returns the events of a case given its id."""
        query = select(CaseStatsEvent).where(CaseStatsEvent.case_stats_id == case_id)
        return list(session.exec(query).all())

    def get_cases(self, 
            session: Session,
            skip: int,
            limit: int,
            bank: str,
            status: list[str] | None,
            order_by: str | None,
            order_desc: bool | None,
        ) -> list[CaseStats]:
        """Filters, orders, and returns a paginated list of cases."""
        query = select(CaseStats)

        if bank:
            query = query.where(CaseStats.bank == bank)
            if title_filter := BANK_FILTER.get(bank):
                query = query.where(CaseStats.title.ilike(f"%{title_filter}%"))
        if status:
            conditions = []
            if "active" in status:
                conditions.append(~CaseStats.legal_stage.in_(["draft", "finished", "archived"]))
            other_statuses = [s for s in status if s != "active"]
            if other_statuses:
                conditions.append(CaseStats.legal_stage.in_(other_statuses))
            query = query.where(or_(*conditions))

        if order_by:
            order_by = order_by.lower()
            if order_by in ("title", "created_at", "events"):
                if order_by == "events":
                    query = query.outerjoin(CaseStatsEvent, CaseStatsEvent.case_stats_id == CaseStats.id).group_by(CaseStats.id)
                    ordering = func.count(CaseStatsEvent.id)
                elif order_by == "created_at":
                    query = query.outerjoin(CaseStatsEvent, CaseStatsEvent.case_stats_id == CaseStats.id)\
                                .group_by(CaseStats.id)
                    ordering = func.min(CaseStatsEvent.creation_date)
                else:
                    ordering = getattr(CaseStats, order_by)
                if order_desc:
                    ordering = ordering.desc()
                else:
                    ordering = ordering.asc()
                query = query.order_by(ordering)

        query = query.offset(skip).limit(min(limit, 100))
        results = list(session.exec(query).all())
        return results

    def get_cases_csv(self, session: Session, bank: str) -> io.BytesIO:
        """Returns the all bank cases information as csv files."""
        query = select(CaseStats).where(CaseStats.bank == bank)

        results = list(session.exec(query).all())
        if not results:
            return []
        
        df = pd.DataFrame([case.model_dump() for case in results]).drop(columns=["id"], errors="ignore")

        df["bank"] = df["bank"].map(BANK_TRANSLATION).fillna(df["bank"])
        df["case_type"] = df["case_type"].map(CASE_TYPE_TRANSLATIONS).fillna(df["case_type"])
        df["legal_stage"] = df["legal_stage"].map(LEGAL_STAGE_TRANSLATIONS).fillna(df["legal_stage"])
        df["result"] = df["result"].map(RESULT_TRANSLATIONS).fillna(df["result"])

        column_order = [
            "title", "case_role", "case_type", "result", "bank", "year", "court_city",
            "court_number", "legal_stage", "amount", "currency",
        ]
        
        column_rename_map = {
            "court_city": "Ciudad del juzgado",
            "year": "Año",
            "legal_stage": "Etapa legal",
            "amount": "Monto",
            "result": "Resultado",
            "bank": "Banco",
            "court_number": "Número de causa",
            "case_role": "Rol",
            "case_type": "Tipo",
            "title": "Caratulado",
            "currency": "Moneda"
        }

        df = df[column_order].rename(columns=column_rename_map)
        if "Moneda" in df.columns:
            df["Moneda"] = df["Moneda"].astype(str).str.upper()

        chunk_size = 10000
        num_chunks = (len(df) // chunk_size) + (1 if len(df) % chunk_size else 0)
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(num_chunks):
                chunk_df = df.iloc[i * chunk_size:(i + 1) * chunk_size]
                csv_buffer = io.StringIO()
                chunk_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                zip_file.writestr(f"casos_p{i + 1}.csv", csv_buffer.getvalue())

        zip_buffer.seek(0)
        return zip_buffer

    def get_probable_case_stats(self, session: Session, case: Case) -> ProbableCaseStats | None:
        case_type = (
            "promissory_note_collection"
            if case.legal_subject == LegalSubject.PROMISSORY_NOTE_COLLECTION
            else case.legal_subject.value
        )

        # Event types for the current case
        events_query = select(CaseEvent.type).where(CaseEvent.case_id == case.id)
        events = session.exec(events_query).all()
        case_legal_stage = map_events_to_legal_stage(events) if events else None

        # Total, compromise, and withdrawal query
        total_query = select(func.count(CaseStats.id)).where(
            CaseStats.case_type == case_type,
            CaseStats.result != "pending"
        )
        total_count = session.exec(total_query).first() or 0

        compromise_query = select(func.count(CaseStats.id)).where(
            CaseStats.case_type == case_type,
            CaseStats.result == "settlement",
        )
        compromise_count = session.exec(compromise_query).first() or 0
        overall_compromise_chance = compromise_count / total_count if total_count > 0 else None

        withdrawal_query = select(func.count(CaseStats.id)).where(
            CaseStats.case_type == case_type,
            CaseStats.result == "desisted",
        )
        withdrawal_count = session.exec(withdrawal_query).first() or 0
        overall_withdrawal_chance = withdrawal_count / total_count if total_count > 0 else None

        similar_total_count = 0
        similar_compromise_chance = None
        similar_withdrawal_chance = None

        if case.amount_currency and case.amount is not None:
            lower_bound = case.amount * 0.8
            upper_bound = case.amount * 1.2

            base_filters = [
                CaseStats.case_type == case_type,
                CaseStats.result != "pending",
                CaseStats.amount.is_not(None),
                CaseStats.currency == case.amount_currency.value,
                CaseStats.amount.between(lower_bound, upper_bound),
            ]

            if case_legal_stage in ["exceptions", "exceptions_response", "demand_notification"]:
                base_filters.append(
                    CaseStats.id.in_(
                        select(CaseStatsEvent.case_stats_id)
                        .where(CaseStatsEvent.type == case_legal_stage)
                    )
                )

            similar_total_query = select(func.count(CaseStats.id)).where(*base_filters)
            similar_total_count = session.exec(similar_total_query).first() or 0

            similar_compromise_query = select(func.count(CaseStats.id)).where(
                *base_filters,
                CaseStats.result == "settlement",
            )
            similar_compromise_count = session.exec(similar_compromise_query).first() or 0

            similar_withdrawal_query = select(func.count(CaseStats.id)).where(
                *base_filters,
                CaseStats.result == "desisted",
            )
            similar_withdrawal_count = session.exec(similar_withdrawal_query).first() or 0

            if similar_total_count > 50:
                similar_compromise_chance = similar_compromise_count / similar_total_count
                similar_withdrawal_chance = similar_withdrawal_count / similar_total_count
        
        compromise_chance = similar_compromise_chance if similar_compromise_chance is not None else overall_compromise_chance
        withdrawal_chance = similar_withdrawal_chance if similar_withdrawal_chance is not None else overall_withdrawal_chance

        # Average duration query
        avg_settlement_query = select(func.avg(CaseStats.duration)).where(
            CaseStats.case_type == case_type,
            CaseStats.result == "settlement"
        )
        avg_settlement_duration = session.exec(avg_settlement_query).first() or 0

        avg_non_settlement_query = select(func.avg(CaseStats.duration)).where(
            CaseStats.case_type == case_type,
            CaseStats.result.not_in(["pending", "desisted", "settlement"])
        )
        avg_non_settlement_duration = session.exec(avg_non_settlement_query).first() or 0

        if avg_non_settlement_duration is not None and avg_settlement_duration is not None:
            days_saved = int(avg_non_settlement_duration - avg_settlement_duration)
            overall_days_to_resolve = max(days_saved, 0)
        else:
            overall_days_to_resolve = None
        
        similar_days_to_resolve = None

        if similar_total_count > 50 and case.amount_currency and case.amount is not None:
            lower_bound = case.amount * 0.8
            upper_bound = case.amount * 1.2
                        
            base_filters = [
                CaseStats.case_type == case_type,
                CaseStats.result.not_in(["pending", "desisted", "settlement"]),
                CaseStats.amount.is_not(None),
                CaseStats.currency == case.amount_currency.value,
                CaseStats.amount.between(lower_bound, upper_bound)
            ]

            if case_legal_stage in ["exceptions", "exceptions_response", "demand_notification"]:
                base_filters.append(
                    CaseStats.id.in_(
                        select(CaseStatsEvent.case_stats_id)
                        .where(CaseStatsEvent.type == case_legal_stage)
                    )
                )

            similar_non_settlement_query = select(func.avg(CaseStats.duration)).where(*base_filters)
            avg_similar_non_settlement_duration = session.exec(similar_non_settlement_query).first() or 0

            similar_settlement_query = select(func.avg(CaseStats.duration)).where(
                *base_filters,
                CaseStats.result == "settlement",
            )
            avg_similar_settlement_duration = session.exec(similar_settlement_query).first() or 0

            similar_days_to_resolve = max(int(avg_similar_non_settlement_duration - avg_similar_settlement_duration), 0)
        
        days_to_resolve = similar_days_to_resolve if similar_days_to_resolve is not None else overall_days_to_resolve

        return ProbableCaseStats(
            compromise_amount_percentage=None, #TODO: Add settlement for amount in CaseStats
            compromise_chance=compromise_chance,
            days_to_resolve=days_to_resolve,
            withdrawal_chance=withdrawal_chance,
        )
