from sqlalchemy import select
from sqlalchemy.orm import Session
from app.crud.base import apply_updates, commit_refresh, schema_to_dict
from app.models.Users.permission_model import Permission
from app.models.Users.role_permission_model import RolePermission
from app.schemas.Users.permission_schema import PermissionCreate, PermissionUpdate
from uuid import UUID
from typing import Optional, List


def get_permissions(db: Session, scope: Optional[str] = None) -> List[Permission]:
    query = select(Permission).order_by(Permission.code)
    if scope is not None:
        query = query.where(Permission.scope == scope)
    return list(db.scalars(query))


def get_permissions_for_role(db: Session, role_id: UUID) -> List[Permission]:
    query = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_code == Permission.code)
        .where(RolePermission.role_id == role_id)
        .order_by(Permission.code)
    )
    return list(db.scalars(query))


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.get(Permission, code)


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    instance = Permission(**schema_to_dict(permission))
    db.add(instance)
    return commit_refresh(db, instance)


def update_permission(db: Session, permission: Permission, update: PermissionUpdate) -> Permission:
    apply_updates(permission, schema_to_dict(update, exclude_unset=True))
    return commit_refresh(db, permission)


def is_permission_assigned(db: Session, code: str) -> bool:
    return db.scalar(
        select(RolePermission.role_id).where(RolePermission.permission_code == code).limit(1)
    ) is not None


def delete_permission(db: Session, permission: Permission) -> None:
    db.delete(permission)
    db.commit()
