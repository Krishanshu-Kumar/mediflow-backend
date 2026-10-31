from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.core.constants import SUPER_ADMIN_ROLE_ID
from app.core.database import get_db
from app.core import messages, status_codes
from app.core.dependencies import is_super_admin, require_permission
from app.crud import permission_crud, role_crud, tenant_crud
from app.models.Users.auth_users_model import AuthUser
from app.models.Users.role_model import Role
from app.schemas.Users.permission_schema import PermissionResponse
from app.schemas.Users.role_schema import (
    RoleCreate,
    RolePermissionsUpdate,
    RoleResponse,
    RoleUpdate,
)

# Super Admin manages roles in every tenant. A hospital user holding the
# `roles.manage` permission manages roles in their own tenant only.
router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)

# Created once so FastAPI resolves it a single time per request.
require_roles_manage = require_permission("roles.manage")


def _get_role_or_404(db: Session, role_id: UUID, current_user: AuthUser) -> Role:
    """Fetch a role; one outside the caller's tenant looks like it doesn't exist."""
    role = role_crud.get_role_by_id(db, role_id)
    if not role or (not is_super_admin(current_user) and role.tenant_id != current_user.tenant_id):
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


def _ensure_not_own_role(role_id: UUID, current_user: AuthUser) -> None:
    """Stops a hospital user locking themselves out by changing their own role."""
    if not is_super_admin(current_user) and role_id == current_user.role_id:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.OWN_ROLE_PROTECTED,
        )


@router.post("/", response_model=RoleResponse, status_code=status_codes.HTTP_201_CREATED)
def create_role(
    role: RoleCreate,
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    if is_super_admin(current_user):
        if role.tenant_id is None:
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail="tenant_id is required",
            )
        tenant_id = role.tenant_id
    else:
        # Hospital users can only create roles in their own tenant.
        if role.tenant_id is not None and role.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status_codes.HTTP_403_FORBIDDEN,
                detail=messages.PERMISSION_REQUIRED,
            )
        tenant_id = current_user.tenant_id

    if not tenant_crud.get_tenant_by_id(db, tenant_id):
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )
    _ensure_name_available(db, tenant_id, role.name)
    return role_crud.create_role(db, role.model_copy(update={"tenant_id": tenant_id}))


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    tenant_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    if not is_super_admin(current_user):
        tenant_id = current_user.tenant_id
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
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    return _get_role_or_404(db, role_id, current_user)


@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(
    role_id: UUID,
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    _get_role_or_404(db, role_id, current_user)
    return permission_crud.get_permissions_for_role(db, role_id)


@router.put("/{role_id}/permissions", response_model=List[PermissionResponse])
def set_role_permissions(
    role_id: UUID,
    payload: RolePermissionsUpdate,
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    """
    Replace the role's permissions with the given list.

    Super Admin can grant any permission. A hospital user can only grant
    tenant-level permissions that they hold themselves, and cannot change
    their own role's permissions.
    """
    _ensure_not_super_admin_role(role_id)
    _ensure_not_own_role(role_id, current_user)
    _get_role_or_404(db, role_id, current_user)

    codes = set(payload.permission_codes)
    known = {p.code: p for p in permission_crud.get_permissions(db)}
    unknown = codes - known.keys()
    if unknown:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.PERMISSION_NOT_FOUND,
        )

    if not is_super_admin(current_user):
        held = {p.code for p in permission_crud.get_permissions_for_role(db, current_user.role_id)}
        if any(known[c].scope != "tenant" or c not in held for c in codes):
            raise HTTPException(
                status_code=status_codes.HTTP_403_FORBIDDEN,
                detail=messages.PERMISSION_NOT_GRANTABLE,
            )

    return permission_crud.set_role_permissions(db, role_id, list(codes))


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    """
    Rename a role. The Super Admin role cannot be modified.
    """
    _ensure_not_super_admin_role(role_id)
    role = _get_role_or_404(db, role_id, current_user)
    if role_update.name is not None:
        _ensure_name_available(db, role.tenant_id, role_update.name, role_id)
    return role_crud.update_role(db, role_id, role_update)


@router.patch("/{role_id}/status", response_model=RoleResponse)
def set_role_status(
    role_id: UUID,
    is_active: bool = Query(..., description="Set active (true) or inactive (false) status"),
    current_user: AuthUser = Depends(require_roles_manage),
    db: Session = Depends(get_db),
):
    """
    Activate or deactivate a role. The Super Admin role cannot be deactivated,
    nor can a role that still has active users.
    """
    _ensure_not_super_admin_role(role_id)
    _get_role_or_404(db, role_id, current_user)
    if not is_active:
        _ensure_not_own_role(role_id, current_user)
        if role_crud.has_active_users(db, role_id):
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=messages.ROLE_HAS_ACTIVE_USERS,
            )
    return role_crud.set_role_active_status(db, role_id, is_active)
