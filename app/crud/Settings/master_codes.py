from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Settings.master_codes import MasterCode


def get_master_code(db: Session, code: int) -> Optional[MasterCode]:
    return db.get(MasterCode, code)


def get_master_codes(
    db: Session,
    category_code: Optional[int] = None,
    active_only: bool = True,
) -> List[MasterCode]:
    query = select(MasterCode).order_by(MasterCode.code)
    if category_code is not None:
        query = query.where(MasterCode.category_code == category_code)
    if active_only:
        query = query.where(MasterCode.is_active)
    return list(db.scalars(query))
