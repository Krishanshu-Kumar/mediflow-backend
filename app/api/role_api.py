from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core import messages
from app.core import status_codes
from app.crud import role_crud
from app.schemas.Users.role_schema import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.post("/", response_model=RoleResponse)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
):
    return role_crud.create_role(db, role)


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return role_crud.get_roles(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    role = role_crud.get_role_by_id(
        db,
        role_id,
    )

    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )

    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
):
    role = role_crud.update_role(
        db,
        role_id,
        role_update,
    )

    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )

    return role


@router.patch("/{role_id}/deactivate", response_model=RoleResponse)
def deactivate_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    role = role_crud.deactivate_role(
        db,
        role_id,
    )

    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )

    return role


@router.patch("/{role_id}/activate", response_model=RoleResponse)
def activate_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    role = role_crud.activate_role(
        db,
        role_id,
    )

    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )

    return role