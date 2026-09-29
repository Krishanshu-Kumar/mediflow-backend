from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.core.constants import SYSTEM_TENANT_ID
from app.core.database import get_db
from app.core import messages, status_codes
from app.core.dependencies import get_current_super_admin
from app.crud import tenant_crud
from app.crud.Settings import master_codes as master_codes_crud
from app.models.Settings.master_codes import MasterCodeCategory
from app.schemas.Users.tenant_schema import TenantCreate, TenantUpdate, TenantResponse

# All routes in this router require Super Admin privileges.
router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
    dependencies=[Depends(get_current_super_admin)],
)


def _ensure_valid_plan(db: Session, plan_code: int) -> None:
    plan = master_codes_crud.get_master_code(db, plan_code)
    if not plan or plan.category_code != MasterCodeCategory.PLAN or not plan.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INVALID_PLAN,
        )


def _ensure_slug_available(db: Session, slug: str, tenant_id: Optional[UUID] = None) -> None:
    existing = tenant_crud.get_tenant_by_slug(db, slug)
    if existing and existing.id != tenant_id:
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.TENANT_SLUG_EXISTS,
        )


def _ensure_not_system_tenant(tenant_id: UUID) -> None:
    if tenant_id == SYSTEM_TENANT_ID:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SYSTEM_TENANT_PROTECTED,
        )


@router.post("/", response_model=TenantResponse, status_code=status_codes.HTTP_201_CREATED)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
):
    _ensure_valid_plan(db, tenant.plan_code)
    _ensure_slug_available(db, tenant.slug)
    return tenant_crud.create_tenant(db, tenant)


@router.get("/", response_model=List[TenantResponse])
def get_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return tenant_crud.get_tenants(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
):
    tenant = tenant_crud.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    tenant_update: TenantUpdate,
    db: Session = Depends(get_db),
):
    """
    Partially update a tenant. The system tenant cannot be modified.
    """
    _ensure_not_system_tenant(tenant_id)
    if tenant_update.plan_code is not None:
        _ensure_valid_plan(db, tenant_update.plan_code)
    if tenant_update.slug is not None:
        _ensure_slug_available(db, tenant_update.slug, tenant_id)

    tenant = tenant_crud.update_tenant(db, tenant_id, tenant_update)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    return tenant


@router.patch("/{tenant_id}/status", response_model=TenantResponse)
def set_tenant_status(
    tenant_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false) status"),
    db: Session = Depends(get_db),
):
    """
    Activate or deactivate a tenant. The system tenant cannot be deactivated.
    """
    _ensure_not_system_tenant(tenant_id)
    tenant = tenant_crud.set_tenant_active_status(db, tenant_id, is_active)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    return tenant
