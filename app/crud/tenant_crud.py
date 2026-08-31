from sqlalchemy.orm import Session
from app.crud.base import (
    create_instance,
    get_by_id,
    get_multi,
    update_fields,
    update_instance,
)
from app.models.Users.tenant_model import Tenant
from app.schemas.Users.tenant_schema import TenantCreate, TenantUpdate
from uuid import UUID
from typing import Optional, List


def set_tenant_active_status(
    db: Session,
    tenant_id: UUID,
    is_active: bool,
) -> Optional[Tenant]:
    return update_fields(db, Tenant, tenant_id, is_active=is_active)


def create_tenant(db: Session, tenant: TenantCreate, created_by: Optional[UUID] = None) -> Tenant:
    """
    Create a new tenant in the database
    """
    return create_instance(db, Tenant, tenant, created_by=created_by)


def get_tenant_by_id(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Get a single tenant by ID
    """
    return get_by_id(db, Tenant, tenant_id)


def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
    """
    Get a tenant by their unique slug
    Useful for subdomain-based tenant identification
    """
    return db.query(Tenant).filter(Tenant.slug == slug).first()


def get_tenants(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[Tenant]:
    """
    Get a list of tenants with pagination
    """
    return get_multi(db, Tenant, skip=skip, limit=limit, active_only=active_only)


def update_tenant(
    db: Session, 
    tenant_id: UUID, 
    tenant_update: TenantUpdate,
    updated_by: Optional[UUID] = None
) -> Optional[Tenant]:
    """
    Update a tenant's information
    """
    return update_instance(db, Tenant, tenant_id, tenant_update, updated_by=updated_by)


def deactivate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Soft delete - mark tenant as inactive
    (We don't hard delete in production systems)
    """
    return set_tenant_active_status(db, tenant_id, False)


def activate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Reactivate a previously deactivated tenant
    """
    return set_tenant_active_status(db, tenant_id, True)


