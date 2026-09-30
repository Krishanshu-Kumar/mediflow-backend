from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    tenant_id: UUID
    name: str = Field(..., min_length=1, max_length=100)


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
