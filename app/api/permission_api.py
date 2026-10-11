from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core import messages, status_codes
from app.core.database import get_db
from app.core.dependencies import get_current_super_admin
from app.crud import permission_crud
from app.models.Users.permission_model import Permission
from app.schemas.Users.permission_schema import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    Scope,
)

# Managed by Super Admin only. A permission only does something once endpoint
# code checks for its code, so add the row and the check together.
router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[Depends(get_current_super_admin)],
)


def _get_permission_or_404(db: Session, code: str) -> Permission:
    permission = permission_crud.get_permission_by_code(db, code)
    if not permission:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.PERMISSION_NOT_FOUND,
        )
    return permission


@router.post("/", response_model=PermissionResponse, status_code=status_codes.HTTP_201_CREATED)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
):
    if permission_crud.get_permission_by_code(db, permission.code):
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.PERMISSION_CODE_EXISTS,
        )
    return permission_crud.create_permission(db, permission)


@router.get("/", response_model=List[PermissionResponse])
def get_permissions(
    scope: Optional[Scope] = None,
    db: Session = Depends(get_db),
):
    return permission_crud.get_permissions(db, scope=scope)


@router.get("/{code}", response_model=PermissionResponse)
def get_permission(
    code: str,
    db: Session = Depends(get_db),
):
    return _get_permission_or_404(db, code)


@router.put("/{code}", response_model=PermissionResponse)
def update_permission(
    code: str,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
):
    """
    Change a permission's description or scope. The code cannot be changed.
    """
    permission = _get_permission_or_404(db, code)
    return permission_crud.update_permission(db, permission, permission_update)


@router.delete("/{code}", status_code=status_codes.HTTP_204_NO_CONTENT)
def delete_permission(
    code: str,
    db: Session = Depends(get_db),
):
    """
    Delete a permission. Refused while any role still holds it.
    """
    permission = _get_permission_or_404(db, code)
    if permission_crud.is_permission_assigned(db, code):
        raise HTTPException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=messages.PERMISSION_IN_USE,
        )
    permission_crud.delete_permission(db, permission)
