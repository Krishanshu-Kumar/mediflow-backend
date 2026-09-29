from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core import messages, status_codes
from app.core.dependencies import get_current_active_user
from app.crud.Settings import master_codes as master_codes_crud
from app.schemas.Settings.master_codes import MasterCodeResponse

# Read-only: master codes are reference data managed through migrations.
router = APIRouter(
    prefix="/settings/master-codes",
    tags=["Master Codes"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=List[MasterCodeResponse])
def get_master_codes(
    category_code: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    List master codes, optionally filtered to one category (e.g. 1000 = plans).
    """
    return master_codes_crud.get_master_codes(
        db,
        category_code=category_code,
        active_only=active_only,
    )


@router.get("/{code}", response_model=MasterCodeResponse)
def get_master_code(
    code: int,
    db: Session = Depends(get_db),
):
    master_code = master_codes_crud.get_master_code(db, code)
    if not master_code:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.MASTER_CODE_NOT_FOUND,
        )
    return master_code
