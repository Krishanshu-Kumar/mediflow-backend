from sqlalchemy.orm import Session
from app.crud.base import (
    create_instance,
    get_by_id,
    get_multi,
    update_fields,
    update_instance,
)
from app.models.Users.role_model import Role
from app.schemas.Users.role_schema import RoleCreate, RoleUpdate
from uuid import UUID
from typing import Optional, List


def set_role_active_status(
    db: Session,
    role_id: UUID,
    is_active: bool,
) -> Optional[Role]:
    return update_fields(db, Role, role_id, is_active=is_active)


def set_role_system_status(
    db: Session,
    role_id: UUID,
    is_system_role: bool,
) -> Optional[Role]:
    return update_fields(db, Role, role_id, is_system_role=is_system_role)


def create_role(
    db: Session,
    role: RoleCreate,
    created_by: Optional[UUID] = None,
) -> Role:
    """
    Create a new role in the database
    """
    return create_instance(db, Role, role, created_by=created_by)


def get_role_by_id(
    db: Session,
    role_id: UUID,
) -> Optional[Role]:
    """
    Get a single role by ID
    """
    return get_by_id(db, Role, role_id)


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
    """
    return get_multi(db, Role, skip=skip, limit=limit, active_only=active_only)


def update_role(
    db: Session,
    role_id: UUID,
    role_update: RoleUpdate,
    updated_by: Optional[UUID] = None,
) -> Optional[Role]:
    """
    Update a role's information
    """
    return update_instance(db, Role, role_id, role_update, updated_by=updated_by)