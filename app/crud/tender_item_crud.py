from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.base import apply_updates, commit_refresh, get_by_id, schema_to_dict
from app.models.Tenders.tender_item_model import TenderItem
from app.schemas.Tenders.tender_item_schema import TenderItemCreate, TenderItemUpdate

ITEM_NO_UNIQUE_CONSTRAINT = "uq_tb_tn_tender_items_tender_id_item_no"
# Two requests adding an item at the same moment can pick the same number;
# the unique constraint rejects one of them and it simply tries again.
MAX_ITEM_NO_ATTEMPTS = 5


def _next_item_no(db: Session, tender_id: UUID) -> int:
    # Soft-deleted items stay in the table, so their numbers are never reused.
    highest = db.scalar(
        select(func.max(TenderItem.item_no)).where(TenderItem.tender_id == tender_id)
    )
    return (highest or 0) + 1


def _is_item_no_conflict(exc: IntegrityError) -> bool:
    diag = getattr(getattr(exc, "orig", None), "diag", None)
    return getattr(diag, "constraint_name", None) == ITEM_NO_UNIQUE_CONSTRAINT


def create_tender_item(
    db: Session,
    tender_id: UUID,
    item_in: TenderItemCreate,
    created_by: Optional[UUID] = None,
) -> TenderItem:
    data = schema_to_dict(item_in)

    for attempt in range(1, MAX_ITEM_NO_ATTEMPTS + 1):
        item = TenderItem(
            **data,
            tender_id=tender_id,
            item_no=_next_item_no(db, tender_id),
            created_by=created_by,
        )
        db.add(item)
        try:
            return commit_refresh(db, item)
        except IntegrityError as exc:
            # commit_refresh has already rolled back
            if attempt == MAX_ITEM_NO_ATTEMPTS or not _is_item_no_conflict(exc):
                raise


def get_tender_item_by_id(db: Session, item_id: UUID) -> Optional[TenderItem]:
    return get_by_id(db, TenderItem, item_id)


def get_tender_items(
    db: Session,
    tender_id: UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[TenderItem]:
    query = select(TenderItem).where(TenderItem.tender_id == tender_id)
    if active_only:
        query = query.where(TenderItem.is_active)
    query = query.order_by(TenderItem.item_no).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def update_tender_item(
    db: Session,
    item: TenderItem,
    item_update: TenderItemUpdate,
    updated_by: Optional[UUID] = None,
) -> TenderItem:
    apply_updates(item, schema_to_dict(item_update, exclude_unset=True))
    item.updated_by = updated_by
    return commit_refresh(db, item)


def set_tender_item_active_status(
    db: Session,
    item: TenderItem,
    is_active: bool,
    updated_by: Optional[UUID] = None,
) -> TenderItem:
    item.is_active = is_active
    item.updated_by = updated_by
    return commit_refresh(db, item)
