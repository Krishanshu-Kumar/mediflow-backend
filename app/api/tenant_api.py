from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.config import settings
from app.core.database import get_db
from app.core import messages, status_codes
from app.core.dependencies import get_current_super_admin
from app.models.Users.auth_users_model import AuthUser
from app.crud import tenant_crud
from app.schemas.Users.tenant_schema import TenantCreate, TenantUpdate, TenantResponse

# All routes in this router require Super Admin privileges.
# get_current_super_admin is enforced at the router level — no need to repeat
# it per-endpoint. Routes that also need the user object (e.g. for audit fields)
# still declare `current_user` explicitly as a typed dependency.
router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
    dependencies=[Depends(get_current_super_admin)],
)


@router.post("/", response_model=TenantResponse, status_code=status_codes.HTTP_201_CREATED)
def create_tenant(
    tenant: TenantCreate,
    current_user: AuthUser = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new tenant. Restricted to System Super Admins.
    """
    return tenant_crud.create_tenant(
        db,
        tenant,
        created_by=UUID(str(current_user.id)),
    )


@router.get("/", response_model=List[TenantResponse])
def get_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    List all tenants. Restricted to System Super Admins.
    """
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
    """
    Get a single tenant by ID. Restricted to System Super Admins.
    """
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
    current_user: AuthUser = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Update tenant details. Restricted to System Super Admins.
    The system master tenant (MEDIFLOW) cannot be modified.
    """
    if tenant_id == settings.SYSTEM_TENANT_ID:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SYSTEM_TENANT_PROTECTED,
        )
    tenant = tenant_crud.update_tenant(
        db,
        tenant_id,
        tenant_update,
        updated_by=UUID(str(current_user.id)),
    )
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
    Activate or deactivate a tenant. Restricted to System Super Admins.
    The system master tenant (MEDIFLOW) cannot be deactivated.
    """
    if tenant_id == settings.SYSTEM_TENANT_ID:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SYSTEM_TENANT_PROTECTED,
        )
    tenant = tenant_crud.set_tenant_active_status(db, tenant_id, is_active)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    return tenant
