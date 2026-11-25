from datetime import date
from typing import List, Optional
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
from app.models.Tenders.tender_model import Tender
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Tenders.tender_schema import (
    TenderCreate,
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


def _ensure_valid_status(db: Session, status_code: int) -> None:
    status = master_codes_crud.get_master_code(db, status_code)
    if (
        not status
        or status.category_code != MasterCodeCategory.TENDER_STATUS
        or not status.is_active
    ):
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INVALID_TENDER_STATUS,
        )


@router.post("/", response_model=TenderResponse, status_code=status_codes.HTTP_201_CREATED)
def create_tender(
    tender_in: TenderCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """
    Create a tender for a tenant. The financial year is the active one that
    covers today's date, and the reference number is generated.
    """
    _ensure_usable_tenant(db, tender_in.tenant_id)
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
    """Partially update a tender, including its status."""
    tender = _get_tender_or_404(db, tender_id)
    if tender_update.status_code is not None:
        _ensure_valid_status(db, tender_update.status_code)
    return tender_crud.update_tender(db, tender, tender_update, updated_by=current_user.id)


@router.patch("/{tender_id}/status", response_model=TenderResponse)
def set_tender_status(
    tender_id: UUID,
    status_code: int = Query(
        ...,
        description="Tender status code: 4001 draft, 4002 published, 4003 closed, 4004 cancelled",
    ),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Change only the status of a tender."""
    tender = _get_tender_or_404(db, tender_id)
    _ensure_valid_status(db, status_code)
    return tender_crud.update_tender(
        db, tender, TenderUpdate(status_code=status_code), updated_by=current_user.id
    )


@router.patch("/{tender_id}/activation", response_model=TenderResponse)
def set_tender_activation(
    tender_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false)"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """Activate or deactivate a tender. Inactive tenders are hidden from the list by default."""
    tender = tender_crud.get_tender_by_id(db, tender_id)
    if not tender:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENDER_NOT_FOUND,
        )
    return tender_crud.set_tender_active_status(db, tender, is_active, updated_by=current_user.id)
