from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core import status_codes, messages
from app.core.dependencies import get_current_active_user
from app.crud import auth_users_crud, role_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import UserUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all users in the currently logged-in user's tenant with pagination.
    """
    return auth_users_crud.get_users(
        db,
        tenant_id=UUID(str(current_user.tenant_id)),
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific user's details. The user must belong to the same tenant.
    """
    user = auth_users_crud.get_user_by_id(db, user_id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:  # SQLAlchemy compares UUID values correctly at runtime
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a user's details. The target user must belong to the same tenant.
    """
    user = auth_users_crud.get_user_by_id(db, user_id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    # If role is updated, verify the new role exists
    if user_update.role_id is not None:
        role = role_crud.get_role_by_id(db, role_id=user_update.role_id)
        if not role:
            raise HTTPException(
                status_code=status_codes.HTTP_404_NOT_FOUND,
                detail=messages.ROLE_NOT_FOUND,
            )

    return auth_users_crud.update_user(
        db,
        db_user=user,
        user_update=user_update,
        updated_by=UUID(str(current_user.id)),
    )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user (soft-delete). Self-deactivation is prohibited.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail="Self-deactivation is not allowed",
        )

    user = auth_users_crud.get_user_by_id(db, user_id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    updated_user = auth_users_crud.deactivate_user(
        db, user_id=user_id, updated_by=UUID(str(current_user.id))
    )
    if not updated_user:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )
    return updated_user


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Reactivate a user. The target user must belong to the same tenant.
    """
    user = auth_users_crud.get_user_by_id(db, user_id=user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    updated_user = auth_users_crud.activate_user(
        db, user_id=user_id, updated_by=UUID(str(current_user.id))
    )
    if not updated_user:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )
    return updated_user
