from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.crud import tenant as tenant_crud
from app.schemas.Users.tenant import TenantCreate, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("/")
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    return tenant_crud.create_tenant(db, tenant)


@router.get("/")
def get_tenants(db: Session = Depends(get_db)):
    return tenant_crud.get_tenants(db)


@router.get("/{tenant_id}")
def get_tenant(tenant_id: UUID, db: Session = Depends(get_db)):
    tenant = tenant_crud.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant