from sqlalchemy.orm import Session
from app.crud.base import apply_updates, commit_refresh, schema_to_dict
from app.models.Users.role_model import Role
from app.schemas.Users.role_schema import RoleCreate, RoleUpdate
from uuid import UUID
from typing import Optional, List


def _set_role_active_status(
    db: Session,
    role_id: UUID,
    is_active: bool,
) -> Optional[Role]:
    db_role = get_role_by_id(db, role_id)

    if not db_role:
        return None

    db_role.is_active = is_active
    return commit_refresh(db, db_role)


def create_role(
    db: Session,
    role: RoleCreate,
    created_by: Optional[UUID] = None,
) -> Role:
    """
    Create a new role in the database
    """
    role_data = schema_to_dict(role)

    if created_by:
        role_data["created_by"] = created_by

    db_role = Role(**role_data)
    db.add(db_role)

    return commit_refresh(db, db_role)


def get_role_by_id(
    db: Session,
    role_id: UUID,
) -> Optional[Role]:
    """
    Get a single role by ID
    """
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(
    db: Session,
    name: str,
) -> Optional[Role]:
    """
    Get a role by its unique name
    """
    return db.query(Role).filter(Role.name == name).first()


def get_roles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[Role]:
    """
    Get a list of roles with pagination

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, only return active roles
    """
    query = db.query(Role)

    if active_only:
        query = query.filter(Role.is_active == True)

    return query.offset(skip).limit(limit).all()


def update_role(
    db: Session,
    role_id: UUID,
    role_update: RoleUpdate,
    updated_by: Optional[UUID] = None,
) -> Optional[Role]:
    """
    Update a role's information
    """
    db_role = get_role_by_id(db, role_id)

    if not db_role:
        return None

    update_data = schema_to_dict(
        role_update,
        exclude_unset=True,
    )

    if updated_by:
        update_data["updated_by"] = updated_by

    apply_updates(db_role, update_data)

    return commit_refresh(db, db_role)


def deactivate_role(
    db: Session,
    role_id: UUID,
) -> Optional[Role]:
    """
    Soft delete - mark role as inactive
    """
    return _set_role_active_status(
        db,
        role_id,
        False,
    )


def activate_role(
    db: Session,
    role_id: UUID,
) -> Optional[Role]:
    """
    Reactivate a previously deactivated role
    """
    return _set_role_active_status(
        db,
        role_id,
        True,
    )