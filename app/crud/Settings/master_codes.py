from sqlalchemy.orm import Session
from app.crud.base import apply_updates, commit_refresh, schema_to_dict
from app.models.Settings.master_codes import MasterCode
from app.schemas.Settings.master_codes import MasterCodeCreate, MasterCodeUpdate
from uuid import UUID
from typing import Optional, List


def _set_master_code_active_status(
    db: Session,
    master_code_id: UUID,
    is_active: bool,
) -> Optional[MasterCode]:
    db_master_code = get_master_code_by_id(db, master_code_id)

    if not db_master_code:
        return None

    db_master_code.is_active = is_active
    return commit_refresh(db, db_master_code)


def create_master_code(
    db: Session,
    master_code: MasterCodeCreate,
    created_by: Optional[UUID] = None,
) -> MasterCode:
    """
    Create a new master code in the database
    """
    master_code_data = schema_to_dict(master_code)

    if created_by:
        master_code_data["created_by"] = created_by

    db_master_code = MasterCode(**master_code_data)
    db.add(db_master_code)

    return commit_refresh(db, db_master_code)


def get_master_code_by_id(
    db: Session,
    master_code_id: UUID,
) -> Optional[MasterCode]:
    """
    Get a single master code by ID
    """
    return db.query(MasterCode).filter(MasterCode.id == master_code_id).first()


def get_master_code_by_code(
    db: Session,
    code: int,
) -> Optional[MasterCode]:
    """
    Get a master code by its unique integer code
    """
    return db.query(MasterCode).filter(MasterCode.code == code).first()


def get_master_code_by_category_value(
    db: Session,
    category_code: int,
    value: str,
) -> Optional[MasterCode]:
    """
    Get a master code by unique category_code and value combination
    """
    return (
        db.query(MasterCode)
        .filter(
            MasterCode.category_code == category_code,
            MasterCode.value == value,
        )
        .first()
    )


def get_master_codes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[MasterCode]:
    """
    Get a list of master codes with pagination

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, only return active master codes
    """
    query = db.query(MasterCode)

    if active_only:
        query = query.filter(MasterCode.is_active)

    return query.offset(skip).limit(limit).all()


def get_master_codes_by_category(
    db: Session,
    category_code: int,
    active_only: bool = True,
) -> List[MasterCode]:
    """
    Get all master codes belonging to a specific category
    """
    query = db.query(MasterCode).filter(MasterCode.category_code == category_code)

    if active_only:
        query = query.filter(MasterCode.is_active)

    return query.order_by(MasterCode.sort_order.asc()).all()


def update_master_code(
    db: Session,
    master_code_id: UUID,
    master_code_update: MasterCodeUpdate,
    updated_by: Optional[UUID] = None,
) -> Optional[MasterCode]:
    """
    Update a master code's information
    """
    db_master_code = get_master_code_by_id(db, master_code_id)

    if not db_master_code:
        return None

    update_data = schema_to_dict(
        master_code_update,
        exclude_unset=True,
    )

    if updated_by:
        update_data["updated_by"] = updated_by

    apply_updates(db_master_code, update_data)

    return commit_refresh(db, db_master_code)


def deactivate_master_code(
    db: Session,
    master_code_id: UUID,
) -> Optional[MasterCode]:
    """
    Soft delete - mark master code as inactive
    """
    return _set_master_code_active_status(
        db,
        master_code_id,
        False,
    )


def activate_master_code(
    db: Session,
    master_code_id: UUID,
) -> Optional[MasterCode]:
    """
    Reactivate a previously deactivated master code
    """
    return _set_master_code_active_status(
        db,
        master_code_id,
        True,
    )
