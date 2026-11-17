from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core import messages, status_codes
from app.core.database import get_db
from app.core.dependencies import get_current_super_admin
from app.crud.Settings import financial_years as financial_years_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Settings.financial_year_schema import (
    FinancialYearCreate,
    FinancialYearResponse,
    FinancialYearUpdate,
)

# All routes in this router require Super Admin privileges.
router = APIRouter(
    prefix="/financial-years",
    tags=["Financial Years"],
    dependencies=[Depends(get_current_super_admin)],
)


def _ensure_label_available(db: Session, label: str) -> None:
    if financial_years_crud.get_financial_year_by_label(db, label):
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.FINANCIAL_YEAR_LABEL_EXISTS,
        )


def _ensure_no_overlap(
    db: Session, start_date: date, end_date: date, exclude_id: Optional[UUID] = None
) -> None:
    overlap = financial_years_crud.get_overlapping_financial_year(
        db, start_date, end_date, exclude_id=exclude_id
    )
    if overlap:
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.FINANCIAL_YEAR_OVERLAP.format(label=overlap.label),
        )


@router.post("/", response_model=FinancialYearResponse, status_code=status_codes.HTTP_201_CREATED)
def create_financial_year(
    financial_year: FinancialYearCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    _ensure_label_available(db, financial_year.label)
    _ensure_no_overlap(db, financial_year.start_date, financial_year.end_date)
    return financial_years_crud.create_financial_year(
        db, financial_year, created_by=current_user.id
    )


@router.get("/", response_model=List[FinancialYearResponse])
def get_financial_years(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return financial_years_crud.get_financial_years(
        db, skip=skip, limit=limit, active_only=active_only
    )


@router.get("/{financial_year_id}", response_model=FinancialYearResponse)
def get_financial_year(
    financial_year_id: UUID,
    db: Session = Depends(get_db),
):
    financial_year = financial_years_crud.get_financial_year_by_id(db, financial_year_id)
    if not financial_year:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.FINANCIAL_YEAR_NOT_FOUND,
        )
    return financial_year


@router.put("/{financial_year_id}", response_model=FinancialYearResponse)
def update_financial_year(
    financial_year_id: UUID,
    financial_year_update: FinancialYearUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """
    Partially update a financial year's dates. The label cannot be changed
    after creation. The dates must stay valid (start before end) and must not
    overlap another active year.
    """
    existing = financial_years_crud.get_financial_year_by_id(db, financial_year_id)
    if not existing:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.FINANCIAL_YEAR_NOT_FOUND,
        )

    # A partial update may send only one date; check the resulting range
    new_start = financial_year_update.start_date or existing.start_date
    new_end = financial_year_update.end_date or existing.end_date
    if new_start >= new_end:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.FINANCIAL_YEAR_INVALID_DATES,
        )
    if existing.is_active:
        _ensure_no_overlap(db, new_start, new_end, exclude_id=financial_year_id)

    return financial_years_crud.update_financial_year(
        db, financial_year_id, financial_year_update, updated_by=current_user.id
    )


@router.patch("/{financial_year_id}/status", response_model=FinancialYearResponse)
def set_financial_year_status(
    financial_year_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false) status"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_super_admin),
):
    """
    Activate or deactivate a financial year. Activating re-checks that its
    dates do not overlap another active year.
    """
    existing = financial_years_crud.get_financial_year_by_id(db, financial_year_id)
    if not existing:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.FINANCIAL_YEAR_NOT_FOUND,
        )
    if is_active and not existing.is_active:
        _ensure_no_overlap(
            db, existing.start_date, existing.end_date, exclude_id=financial_year_id
        )
    return financial_years_crud.set_financial_year_active_status(
        db, financial_year_id, is_active, updated_by=current_user.id
    )
