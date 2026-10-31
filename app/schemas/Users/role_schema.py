from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    """Super Admin must give tenant_id; for a hospital user it is their own tenant."""
    tenant_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)


class RolePermissionsUpdate(BaseModel):
    """The complete set of permission codes the role should hold."""
    permission_codes: List[str]


class RoleUpdate(BaseModel):
    """
    A role can't move to another tenant, so only the name is editable.
    Activation is done through the /status endpoint only.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
