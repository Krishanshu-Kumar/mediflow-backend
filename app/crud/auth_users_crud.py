from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List
from uuid import UUID

from app.crud.base import apply_updates, commit_refresh, schema_to_dict
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: UUID) -> Optional[AuthUser]:
    """
    Retrieve a user by their UUID.
    """
    return db.query(AuthUser).filter(AuthUser.id == user_id).first()


def get_user_by_email_and_tenant(
    db: Session,
    email: str,
    tenant_id: UUID,
) -> Optional[AuthUser]:
    """
    Retrieve a user by their email address and tenant ID.
    (Email is unique per tenant, not globally).
    """
    return (
        db.query(AuthUser)
        .filter(AuthUser.email == email, AuthUser.tenant_id == tenant_id)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
    created_by: Optional[UUID] = None,
) -> AuthUser:
    """
    Create a new user, hashing their password.
    """
    user_data = schema_to_dict(user)

    # Hash the password and save to hashed_password field
    password = user_data.pop("password")
    user_data["hashed_password"] = get_password_hash(password)

    if created_by:
        user_data["created_by"] = created_by
        user_data["updated_by"] = created_by

    db_user = AuthUser(**user_data)
    db.add(db_user)

    return commit_refresh(db, db_user)


def get_users(
    db: Session,
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[AuthUser]:
    """
    Get a list of users for a specific tenant with pagination.
    """
    query = db.query(AuthUser).filter(AuthUser.tenant_id == tenant_id)
    if active_only:
        query = query.filter(AuthUser.is_active == True)

    return query.offset(skip).limit(limit).all()


def update_user(
    db: Session,
    db_user: AuthUser,
    user_update: UserUpdate,
    updated_by: Optional[UUID] = None,
) -> AuthUser:
    """
    Update a user's details. If password is provided, it is hashed,
    and password_changed_at is updated.
    """
    update_data = schema_to_dict(user_update, exclude_unset=True)

    if "password" in update_data:
        password = update_data.pop("password")
        if password:
            update_data["hashed_password"] = get_password_hash(password)
            update_data["password_changed_at"] = func.now()

    if updated_by:
        update_data["updated_by"] = updated_by

    apply_updates(db_user, update_data)
    return commit_refresh(db, db_user)


def _set_user_active_status(
    db: Session,
    user_id: UUID,
    is_active: bool,
    updated_by: Optional[UUID] = None,
) -> Optional[AuthUser]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.is_active = is_active
    if updated_by:
        db_user.updated_by = updated_by
    return commit_refresh(db, db_user)


def deactivate_user(
    db: Session,
    user_id: UUID,
    updated_by: Optional[UUID] = None,
) -> Optional[AuthUser]:
    """
    Deactivate (soft delete) a user.
    """
    return _set_user_active_status(db, user_id, False, updated_by)


def activate_user(
    db: Session,
    user_id: UUID,
    updated_by: Optional[UUID] = None,
) -> Optional[AuthUser]:
    """
    Reactivate a deactivated user.
    """
    return _set_user_active_status(db, user_id, True, updated_by)


def authenticate_user(
    db: Session,
    email: str,
    tenant_id: UUID,
    password: str,
) -> Optional[AuthUser]:
    """
    Authenticate a user by email, tenant_id, and password.
    Updates last_login_at on success.
    """
    db_user = get_user_by_email_and_tenant(db, email=email, tenant_id=tenant_id)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None

    db_user.last_login_at = func.now()
    return commit_refresh(db, db_user)
