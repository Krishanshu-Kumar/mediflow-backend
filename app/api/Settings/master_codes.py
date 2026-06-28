from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core import messages
from app.core import status_codes
from app.crud.Settings import master_codes as master_codes_crud
from app.schemas.Settings.master_codes import (
    MasterCodeCreate,
    MasterCodeUpdate,
    MasterCodeResponse,
)

router = APIRouter(
    prefix="/settings/master-codes",
    tags=["Master Codes"],
)


@router.post("/", response_model=MasterCodeResponse, status_code=status_codes.HTTP_201_CREATED)
def create_master_code(
    master_code: MasterCodeCreate,
    db: Session = Depends(get_db),
):
    return master_codes_crud.create_master_code(db, master_code)


@router.get("/", response_model=List[MasterCodeResponse])
def get_master_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return master_codes_crud.get_master_codes(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )


@router.get("/{master_code_id}", response_model=MasterCodeResponse)
def get_master_code(
    master_code_id: UUID,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.get_master_code_by_id(
        db,
        master_code_id,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code


@router.get("/code/{code}", response_model=MasterCodeResponse)
def get_master_code_by_code(
    code: int,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.get_master_code_by_code(
        db,
        code,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code


@router.get("/category/{category_code}", response_model=List[MasterCodeResponse])
def get_master_codes_by_category(
    category_code: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    return master_codes_crud.get_master_codes_by_category(
        db,
        category_code=category_code,
        active_only=active_only,
    )


@router.get("/category/{category_code}/value/{value}", response_model=MasterCodeResponse)
def get_master_code_by_category_value(
    category_code: int,
    value: str,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.get_master_code_by_category_value(
        db,
        category_code=category_code,
        value=value,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code


@router.put("/{master_code_id}", response_model=MasterCodeResponse)
def update_master_code(
    master_code_id: UUID,
    master_code_update: MasterCodeUpdate,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.update_master_code(
        db,
        master_code_id,
        master_code_update,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code


@router.patch("/{master_code_id}/deactivate", response_model=MasterCodeResponse)
def deactivate_master_code(
    master_code_id: UUID,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.deactivate_master_code(
        db,
        master_code_id,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code


@router.patch("/{master_code_id}/activate", response_model=MasterCodeResponse)
def activate_master_code(
    master_code_id: UUID,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.activate_master_code(
        db,
        master_code_id,
    )

    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )

    return master_code
