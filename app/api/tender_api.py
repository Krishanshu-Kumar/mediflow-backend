from datetime import date, datetime, timezone
from typing import Iterable, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core import messages, status_codes
from app.core.database import get_db
from app.core.dependencies import get_current_super_admin
from app.crud import tender_crud, tenant_crud
from app.crud.Settings import financial_years as financial_years_crud
from app.crud.Settings import master_codes as master_codes_crud
from app.models.Settings.master_codes import MasterCodeCategory
from app.models.Tenders.tender_model import Tender, TenderStatus
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Tenders.tender_schema import (
    TenderCreate,
    TenderItemCreate,
    TenderResponse,
    TenderUpdate,
)

# All routes in this router require Super Admin privileges.
router = APIRouter(
    prefix="/tenders",
    tags=["Tenders"],
    dependencies=[Depends(get_current_super_admin)],
)


def _get_tender_or_404(db: Session, tender_id: UUID) -> Tender:
    """Deleted (inactive) tenders are treated as not found."""
    tender = tender_crud.get_tender_by_id(db, tender_id)
    if not tender or not tender.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENDER_NOT_FOUND,
        )
    return tender


def _ensure_usable_tenant(db: Session, tenant_id: UUID) -> None:
    tenant = tenant_crud.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    if not tenant.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INACTIVE_TENANT,
        )


def _ensure_valid_item_types(db: Session, items: Iterable[TenderItemCreate]) -> None:
    for code in {item.item_type_code for item in items}:
        item_type = master_codes_crud.get_master_code(db, code)
        if (
            not item_type
            or item_type.category_code != MasterCodeCategory.TENDER_ITEM_TYPE
            or not item_type.is_active
        ):
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail=messages.INVALID_ITEM_TYPE,
            )


def _ensure_draft(tender: Tender) -> None:
    if tender.status_code != TenderStatus.DRAFT:
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.TENDER_NOT_DRAFT,
        )


def _ensure_can_move(tender: Tender, allowed_from: set, action: str) -> None:
    if tender.status_code not in allowed_from:
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.TENDER_INVALID_TRANSITION.format(
                action=action, status=tender.status.display_name.lower()
            ),
        )


@router.post("/", response_model=TenderResponse, status_code=status_codes.HTTP_201_CREATED)
def create_tender(
    tender_in: TenderCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """
    Create a draft tender for a tenant. The financial year is the active one
    that covers today's date, and the reference number is generated.
    """
    _ensure_usable_tenant(db, tender_in.tenant_id)
    _ensure_valid_item_types(db, tender_in.items)

    financial_year = financial_years_crud.get_financial_year_for_date(db, date.today())
    if not financial_year:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.NO_ACTIVE_FINANCIAL_YEAR,
        )
    return tender_crud.create_tender(db, tender_in, financial_year, created_by=current_user.id)


@router.get("/", response_model=List[TenderResponse])
def get_tenders(
    tenant_id: Optional[UUID] = Query(None, description="Only this tenant's tenders"),
    status_code: Optional[int] = Query(None, description="Only tenders with this status code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    if tenant_id is not None and not tenant_crud.get_tenant_by_id(db, tenant_id):
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    return tender_crud.get_tenders(
        db,
        tenant_id=tenant_id,
        status_code=status_code,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
):
    return _get_tender_or_404(db, tender_id)


@router.put("/{tender_id}", response_model=TenderResponse)
def update_tender(
    tender_id: UUID,
    tender_update: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """
    Partially update a draft tender. If `items` is sent it replaces the whole
    item list. Tenders that are no longer drafts are read-only.
    """
    tender = _get_tender_or_404(db, tender_id)
    _ensure_draft(tender)
    if tender_update.items is not None:
        _ensure_valid_item_types(db, tender_update.items)
    return tender_crud.update_tender(db, tender, tender_update, updated_by=current_user.id)


@router.delete("/{tender_id}", status_code=status_codes.HTTP_204_NO_CONTENT)
def delete_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Soft-delete a draft tender. Tenders that were published are cancelled instead."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_draft(tender)
    tender_crud.soft_delete_tender(db, tender, updated_by=current_user.id)


@router.post("/{tender_id}/publish", response_model=TenderResponse)
def publish_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Draft -> Published. Needs a deadline in the future and at least one item."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_can_move(tender, {TenderStatus.DRAFT}, "publish")

    if tender.deadline is None:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.TENDER_DEADLINE_REQUIRED,
        )
    if tender.deadline <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.TENDER_DEADLINE_PAST,
        )
    if not tender.items:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.TENDER_ITEMS_REQUIRED,
        )
    return tender_crud.set_tender_status(
        db, tender, TenderStatus.PUBLISHED, updated_by=current_user.id
    )


@router.post("/{tender_id}/close", response_model=TenderResponse)
def close_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Published -> Closed. Closing is manual; the deadline does not close a tender."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_can_move(tender, {TenderStatus.PUBLISHED}, "close")
    return tender_crud.set_tender_status(
        db, tender, TenderStatus.CLOSED, updated_by=current_user.id
    )


@router.post("/{tender_id}/cancel", response_model=TenderResponse)
def cancel_tender(
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Draft, Published or Closed -> Cancelled. Cancelled is final."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_can_move(
        tender,
        {TenderStatus.DRAFT, TenderStatus.PUBLISHED, TenderStatus.CLOSED},
        "cancel",
    )
    return tender_crud.set_tender_status(
        db, tender, TenderStatus.CANCELLED, updated_by=current_user.id
    )
