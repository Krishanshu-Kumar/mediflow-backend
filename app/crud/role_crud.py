from sqlalchemy import select
from sqlalchemy.orm import Session
from app.crud.base import (
    create_instance,
    get_by_id,
    update_fields,
    update_instance,
)
from app.models.Users.role_model import Role
from app.schemas.Users.role_schema import RoleCreate, RoleUpdate
from uuid import UUID
from typing import Optional, List


def create_role(db: Session, role: RoleCreate) -> Role:
    return create_instance(db, Role, role)


def get_role_by_id(db: Session, role_id: UUID) -> Optional[Role]:
    return get_by_id(db, Role, role_id)


def get_role_by_name(db: Session, tenant_id: UUID, name: str) -> Optional[Role]:
    return db.scalar(select(Role).where(Role.tenant_id == tenant_id, Role.name == name))


def get_roles(
    db: Session,
    tenant_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[Role]:
    query = select(Role).order_by(Role.name)
    if tenant_id is not None:
        query = query.where(Role.tenant_id == tenant_id)
    if active_only:
        query = query.where(Role.is_active)
    return list(db.scalars(query.offset(skip).limit(limit)))


def update_role(
    db: Session,
    role_id: UUID,
    role_update: RoleUpdate,
) -> Optional[Role]:
    return update_instance(db, Role, role_id, role_update)


def set_role_active_status(
    db: Session,
    role_id: UUID,
    is_active: bool,
) -> Optional[Role]:
    return update_fields(db, Role, role_id, is_active=is_active)
