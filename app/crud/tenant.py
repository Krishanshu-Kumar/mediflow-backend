from sqlalchemy.orm import Session
from app.models.Users.tenant import Tenant
from app.schemas.Users.tenant import TenantCreate, TenantUpdate
from uuid import UUID
from typing import Optional, List


def create_tenant(db: Session, tenant: TenantCreate, created_by: Optional[UUID] = None) -> Tenant:
    """
    Create a new tenant in the database
    """
    # Convert schema to dict and add created_by if provided
    tenant_data = tenant.dict()
    if created_by:
        tenant_data["created_by"] = created_by
    
    # Create the SQLAlchemy model instance
    db_tenant = Tenant(**tenant_data)
    
    # Add to session and commit
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)  # Refresh to get database-generated values (id, created_at, etc.)
    
    return db_tenant


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
    # Get the existing tenant
    db_tenant = get_tenant_by_id(db, tenant_id)
    
    if not db_tenant:
        return None
    
    # Update only the fields that were provided (exclude_unset=True)
    update_data = tenant_update.dict(exclude_unset=True)
    
    # Add updated_by if provided
    if updated_by:
        update_data["updated_by"] = updated_by
    
    # Apply updates
    for key, value in update_data.items():
        setattr(db_tenant, key, value)
    
    db.commit()
    db.refresh(db_tenant)
    
    return db_tenant


def deactivate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Soft delete - mark tenant as inactive
    (We don't hard delete in production systems)
    """
    db_tenant = get_tenant_by_id(db, tenant_id)
    
    if not db_tenant:
        return None
    
    db_tenant.is_active = False
    db.commit()
    db.refresh(db_tenant)
    
    return db_tenant


def activate_tenant(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    """
    Reactivate a previously deactivated tenant
    """
    db_tenant = get_tenant_by_id(db, tenant_id)
    
    if not db_tenant:
        return None
    
    db_tenant.is_active = True
    db.commit()
    db.refresh(db_tenant)
    
    return db_tenant