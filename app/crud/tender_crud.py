from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.base import apply_updates, commit_refresh, get_by_id, schema_to_dict
from app.models.Settings.financial_year_model import FinancialYear
from app.models.Tenders.tender_model import Tender, TenderItem, TenderStatus
from app.schemas.Tenders.tender_schema import TenderCreate, TenderUpdate

REFERENCE_UNIQUE_CONSTRAINT = "uq_tb_tn_tenders_tenant_id_reference_no"
# Two requests creating a tender at the same moment can pick the same number;
# the unique constraint rejects one of them and it simply tries again.
MAX_REFERENCE_ATTEMPTS = 5


def _build_items(items: List[dict]) -> List[TenderItem]:
    return [TenderItem(line_no=index, **item) for index, item in enumerate(items, start=1)]


def _next_reference_no(db: Session, tenant_id: UUID, financial_year: FinancialYear) -> str:
    # Soft-deleted tenders stay in the table, so their numbers are never reused
    count = db.scalar(
        select(func.count())
        .select_from(Tender)
        .where(
            Tender.tenant_id == tenant_id,
            Tender.financial_year_id == financial_year.id,
        )
    )
    return f"TND-{financial_year.label}-{count + 1:04d}"


def _is_reference_conflict(exc: IntegrityError) -> bool:
    diag = getattr(getattr(exc, "orig", None), "diag", None)
    return getattr(diag, "constraint_name", None) == REFERENCE_UNIQUE_CONSTRAINT


def create_tender(
    db: Session,
    tender_in: TenderCreate,
    financial_year: FinancialYear,
    created_by: Optional[UUID] = None,
) -> Tender:
    data = schema_to_dict(tender_in)
    items = data.pop("items")

    for attempt in range(1, MAX_REFERENCE_ATTEMPTS + 1):
        tender = Tender(
            **data,
            financial_year_id=financial_year.id,
            reference_no=_next_reference_no(db, tender_in.tenant_id, financial_year),
            items=_build_items(items),
            created_by=created_by,
        )
        db.add(tender)
        try:
            return commit_refresh(db, tender)
        except IntegrityError as exc:
            # commit_refresh has already rolled back
            if attempt == MAX_REFERENCE_ATTEMPTS or not _is_reference_conflict(exc):
                raise


def get_tender_by_id(db: Session, tender_id: UUID) -> Optional[Tender]:
    return get_by_id(db, Tender, tender_id)


def get_tenders(
    db: Session,
    tenant_id: Optional[UUID] = None,
    status_code: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[Tender]:
    query = select(Tender)
    if tenant_id is not None:
        query = query.where(Tender.tenant_id == tenant_id)
    if status_code is not None:
        query = query.where(Tender.status_code == status_code)
    if active_only:
        query = query.where(Tender.is_active)
    query = query.order_by(Tender.created_at.desc(), Tender.reference_no).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def update_tender(
    db: Session,
    tender: Tender,
    tender_update: TenderUpdate,
    updated_by: Optional[UUID] = None,
) -> Tender:
    data = schema_to_dict(tender_update, exclude_unset=True)
    items = data.pop("items", None)
    apply_updates(tender, data)
    if items is not None:
        # Replaces the whole list; the old rows are deleted as orphans
        tender.items = _build_items(items)
    tender.updated_by = updated_by
    return commit_refresh(db, tender)


def set_tender_status(
    db: Session,
    tender: Tender,
    status: TenderStatus,
    updated_by: Optional[UUID] = None,
) -> Tender:
    tender.status_code = int(status)
    tender.updated_by = updated_by
    return commit_refresh(db, tender)


def soft_delete_tender(
    db: Session,
    tender: Tender,
    updated_by: Optional[UUID] = None,
) -> Tender:
    tender.is_active = False
    tender.updated_by = updated_by
    return commit_refresh(db, tender)
