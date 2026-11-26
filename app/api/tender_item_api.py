from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.tender_api import _get_tender_or_404
from app.core import messages, status_codes
from app.core.database import get_db
from app.core.dependencies import get_current_super_admin
from app.crud import tender_item_crud
from app.crud.Settings import master_codes as master_codes_crud
from app.models.Settings.master_codes import MasterCodeCategory
from app.models.Tenders.tender_item_model import TenderItem
from app.models.Tenders.tender_model import Tender, TenderStatus
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Tenders.tender_item_schema import (
    TenderItemCreate,
    TenderItemResponse,
    TenderItemUpdate,
)

# All routes in this router require Super Admin privileges.
router = APIRouter(
    prefix="/tenders/{tender_id}/items",
    tags=["Tender Items"],
    dependencies=[Depends(get_current_super_admin)],
)


def _get_item_or_404(db: Session, tender_id: UUID, item_id: UUID) -> TenderItem:
    item = tender_item_crud.get_tender_item_by_id(db, item_id)
    if not item or item.tender_id != tender_id:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENDER_ITEM_NOT_FOUND,
        )
    return item


def _ensure_tender_editable(tender: Tender) -> None:
    """Items can only be added or changed while the tender is a draft."""
    if tender.status_code != TenderStatus.DRAFT:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.TENDER_ITEMS_LOCKED,
        )


def _ensure_valid_item_type(db: Session, item_type_code: int) -> None:
    item_type = master_codes_crud.get_master_code(db, item_type_code)
    if (
        not item_type
        or item_type.category_code != MasterCodeCategory.TENDER_ITEM_TYPE
        or not item_type.is_active
    ):
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INVALID_TENDER_ITEM_TYPE,
        )


@router.post("/", response_model=TenderItemResponse, status_code=status_codes.HTTP_201_CREATED)
def create_tender_item(
    tender_id: UUID,
    item_in: TenderItemCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Add an item to a draft tender. The item number is generated."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_tender_editable(tender)
    _ensure_valid_item_type(db, item_in.item_type_code)
    return tender_item_crud.create_tender_item(db, tender_id, item_in, created_by=current_user.id)


@router.get("/", response_model=List[TenderItemResponse])
def get_tender_items(
    tender_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    _get_tender_or_404(db, tender_id)
    return tender_item_crud.get_tender_items(
        db, tender_id, skip=skip, limit=limit, active_only=active_only
    )


@router.get("/{item_id}", response_model=TenderItemResponse)
def get_tender_item(
    tender_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
):
    _get_tender_or_404(db, tender_id)
    return _get_item_or_404(db, tender_id, item_id)


@router.put("/{item_id}", response_model=TenderItemResponse)
def update_tender_item(
    tender_id: UUID,
    item_id: UUID,
    item_update: TenderItemUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Partially update an item of a draft tender."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_tender_editable(tender)
    item = _get_item_or_404(db, tender_id, item_id)
    if item_update.item_type_code is not None:
        _ensure_valid_item_type(db, item_update.item_type_code)
    return tender_item_crud.update_tender_item(db, item, item_update, updated_by=current_user.id)


@router.patch("/{item_id}/activation", response_model=TenderItemResponse)
def set_tender_item_activation(
    tender_id: UUID,
    item_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false)"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Activate or deactivate an item of a draft tender. Inactive items are hidden from the list by default."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_tender_editable(tender)
    item = _get_item_or_404(db, tender_id, item_id)
    return tender_item_crud.set_tender_item_active_status(
        db, item, is_active, updated_by=current_user.id
    )
