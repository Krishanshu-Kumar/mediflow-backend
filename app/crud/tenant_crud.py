from sqlalchemy.orm import Session
from app.crud.base import apply_updates, commit_refresh, schema_to_dict
from app.models.Users.tenant_model import Tenant
from app.schemas.Users.tenant_schema import TenantCreate, TenantUpdate
from uuid import UUID
from typing import Optional, List


def _set_tenant_active_status(
    db: Session,
    tenant_id: UUID,
    is_active: bool,
) -> Optional[Tenant]:
    db_tenant = get_tenant_by_id(db, tenant_id)

    if not db_tenant:
        return None

    db_tenant.is_active = is_active
    return commit_refresh(db, db_tenant)


def create_tenant(db: Session, tenant: TenantCreate, created_by: Optional[UUID] = None) -> Tenant:
    """
    Create a new tenant in the database
    """
    tenant_data = schema_to_dict(tenant)
    if created_by:
        tenant_data["created_by"] = created_by

    db_tenant = Tenant(**tenant_data)
    db.add(db_tenant)
    return commit_refresh(db, db_tenant)


def get_tenant_by_id(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Get a single tenant by ID
    """
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


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
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        active_only: If True, only return active tenants
    """
    query = db.query(Tenant)
    
    if active_only:
        query = query.filter(Tenant.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def update_tenant(
    db: Session, 
    tenant_id: UUID, 
    tenant_update: TenantUpdate,
    updated_by: Optional[UUID] = None
) -> Optional[Tenant]:
    """
    Update a tenant's information
    """
    db_tenant = get_tenant_by_id(db, tenant_id)

    if not db_tenant:
        return None

    update_data = schema_to_dict(tenant_update, exclude_unset=True)

    if updated_by:
        update_data["updated_by"] = updated_by

    apply_updates(db_tenant, update_data)
    return commit_refresh(db, db_tenant)


def deactivate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Soft delete - mark tenant as inactive
    (We don't hard delete in production systems)
    """
    return _set_tenant_active_status(db, tenant_id, False)


def activate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Reactivate a previously deactivated tenant
    """
    return _set_tenant_active_status(db, tenant_id, True)
