from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import (
    create_instance,
    get_by_id,
    get_multi,
    update_fields,
    update_instance,
)
from app.models.Settings.financial_year_model import FinancialYear
from app.schemas.Settings.financial_year_schema import (
    FinancialYearCreate,
    FinancialYearUpdate,
)


def create_financial_year(
    db: Session,
    financial_year: FinancialYearCreate,
    created_by: Optional[UUID] = None,
) -> FinancialYear:
    return create_instance(db, FinancialYear, financial_year, created_by=created_by)


def get_financial_year_by_id(db: Session, financial_year_id: UUID) -> Optional[FinancialYear]:
    return get_by_id(db, FinancialYear, financial_year_id)


def get_financial_year_by_label(db: Session, label: str) -> Optional[FinancialYear]:
    return db.scalar(select(FinancialYear).where(FinancialYear.label == label))


def get_financial_year_for_date(db: Session, on_date: date) -> Optional[FinancialYear]:
    """The active financial year that contains `on_date`, if any."""
    return db.scalar(
        select(FinancialYear).where(
            FinancialYear.is_active,
            FinancialYear.start_date <= on_date,
            FinancialYear.end_date >= on_date,
        )
    )


def get_overlapping_financial_year(
    db: Session,
    start_date: date,
    end_date: date,
    exclude_id: Optional[UUID] = None,
) -> Optional[FinancialYear]:
    """Another active year whose date range overlaps [start_date, end_date]."""
    query = select(FinancialYear).where(
        FinancialYear.is_active,
        FinancialYear.start_date <= end_date,
        FinancialYear.end_date >= start_date,
    )
    if exclude_id:
        query = query.where(FinancialYear.id != exclude_id)
    return db.scalars(query).first()


def get_financial_years(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[FinancialYear]:
    return get_multi(db, FinancialYear, skip=skip, limit=limit, active_only=active_only)


def update_financial_year(
    db: Session,
    financial_year_id: UUID,
    financial_year_update: FinancialYearUpdate,
    updated_by: Optional[UUID] = None,
) -> Optional[FinancialYear]:
    return update_instance(
        db, FinancialYear, financial_year_id, financial_year_update, updated_by=updated_by
    )


def set_financial_year_active_status(
    db: Session,
    financial_year_id: UUID,
    is_active: bool,
    updated_by: Optional[UUID] = None,
) -> Optional[FinancialYear]:
    return update_fields(
        db, FinancialYear, financial_year_id, is_active=is_active, updated_by=updated_by
    )
