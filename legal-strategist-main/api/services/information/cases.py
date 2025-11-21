from sqlmodel import func, select, or_

from database.ext_db import Session
from models.sql import Case, CaseEvent, CaseStatus


class CaseRetriever:
    """Cases retriever."""

    def get_case_count(self, session: Session, status: list[str] | None) -> int:
        """Returns the amount of cases that satisfy the filters."""
        query = select(func.count(Case.id))
        
        if status:
            conditions = []
            if "active" in status:
                conditions.append(~Case.status.in_([CaseStatus.DRAFT, CaseStatus.FINISHED, CaseStatus.ARCHIVED]))
            other_statuses = [s for s in status if s != CaseStatus.ACTIVE]
            if other_statuses:
                conditions.append(Case.status.in_(other_statuses))
            query = query.where(or_(*conditions))
        count = session.exec(query).first()
        return count or 0

    def get_cases(self, 
            session: Session,
            skip: int,
            limit: int,
            status: list[str] | None,
            order_by: str | None,
            order_desc: bool | None,
        ) -> list[Case]:
        """Filters, orders, and returns a paginated list of cases."""
        query = select(Case)

        if status:
            conditions = []
            if "active" in status:
                conditions.append(~Case.status.in_([CaseStatus.DRAFT, CaseStatus.FINISHED, CaseStatus.ARCHIVED]))
            other_statuses = [s for s in status if s != CaseStatus.ACTIVE]
            if other_statuses:
                conditions.append(Case.status.in_(other_statuses))
            query = query.where(or_(*conditions))

        if order_by:
            order_by = order_by.lower()
            if order_by in ("title", "created_at", "events"):
                if order_by == "events":
                    query = query.outerjoin(CaseEvent, CaseEvent.case_id == Case.id).group_by(Case.id)
                    ordering = func.count(CaseEvent.id)
                else:
                    ordering = getattr(Case, order_by)
                if order_desc:
                    ordering = ordering.desc()
                else:
                    ordering = ordering.asc()
                query = query.order_by(ordering)

        query = query.offset(skip).limit(min(limit, 100))
        results = list(session.exec(query).all())
        return results
