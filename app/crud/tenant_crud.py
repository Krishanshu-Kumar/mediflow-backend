from sqlalchemy import select
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


def create_tenant(db: Session, tenant: TenantCreate) -> Tenant:
    return create_instance(db, Tenant, tenant)


def get_tenant_by_id(db: Session, tenant_id: UUID) -> Optional[Tenant]:
    return get_by_id(db, Tenant, tenant_id)


def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
    return db.scalar(select(Tenant).where(Tenant.slug == slug))


def get_tenants(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[Tenant]:
    return get_multi(db, Tenant, skip=skip, limit=limit, active_only=active_only)


def update_tenant(
    db: Session,
    tenant_id: UUID,
    tenant_update: TenantUpdate,
) -> Optional[Tenant]:
    return update_instance(db, Tenant, tenant_id, tenant_update)


def set_tenant_active_status(
    db: Session,
    tenant_id: UUID,
    is_active: bool,
) -> Optional[Tenant]:
    return update_fields(db, Tenant, tenant_id, is_active=is_active)
