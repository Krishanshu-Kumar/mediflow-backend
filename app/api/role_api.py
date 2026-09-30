from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.core.constants import SUPER_ADMIN_ROLE_ID
from app.core.database import get_db
from app.core import messages, status_codes
from app.core.dependencies import get_current_super_admin
from app.crud import role_crud, tenant_crud
from app.models.Users.role_model import Role
from app.schemas.Users.role_schema import RoleCreate, RoleUpdate, RoleResponse

# All routes in this router require Super Admin privileges.
# Tenant admins managing their own roles comes with users + login.
router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(get_current_super_admin)],
)


def _get_role_or_404(db: Session, role_id: UUID) -> Role:
    role = role_crud.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )
    return role


def _ensure_name_available(db: Session, tenant_id: UUID, name: str, role_id: Optional[UUID] = None) -> None:
    existing = role_crud.get_role_by_name(db, tenant_id, name)
    if existing and existing.id != role_id:
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.ROLE_NAME_EXISTS,
        )


def _ensure_not_super_admin_role(role_id: UUID) -> None:
    if role_id == SUPER_ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SUPER_ADMIN_ROLE_PROTECTED,
        )


@router.post("/", response_model=RoleResponse, status_code=status_codes.HTTP_201_CREATED)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
):
    if not tenant_crud.get_tenant_by_id(db, role.tenant_id):
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    _ensure_name_available(db, role.tenant_id, role.name)
    return role_crud.create_role(db, role)


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    tenant_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return role_crud.get_roles(
        db,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    return _get_role_or_404(db, role_id)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
):
    """
    Rename a role. The Super Admin role cannot be modified.
    """
    _ensure_not_super_admin_role(role_id)
    role = _get_role_or_404(db, role_id)
    if role_update.name is not None:
        _ensure_name_available(db, role.tenant_id, role_update.name, role_id)
    return role_crud.update_role(db, role_id, role_update)


@router.patch("/{role_id}/status", response_model=RoleResponse)
def set_role_status(
    role_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false) status"),
    db: Session = Depends(get_db),
):
    """
    Activate or deactivate a role. The Super Admin role cannot be deactivated.
    """
    _ensure_not_super_admin_role(role_id)
    _get_role_or_404(db, role_id)
    return role_crud.set_role_active_status(db, role_id, is_active)
