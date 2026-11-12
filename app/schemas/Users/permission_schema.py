from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Scope = Literal["platform", "tenant"]


class PermissionCreate(BaseModel):
    # "resource.action"; same format the database enforces.
    # resource and action are derived from it, not sent separately.
    code: str = Field(..., max_length=100, pattern=r"^[a-z0-9_]+\.[a-z0-9_]+$")
    description: str = Field(..., min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    scope: Scope


class PermissionUpdate(BaseModel):
    """The code is the key that roles and endpoints refer to, so it can't change."""
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    scope: Optional[Scope] = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    resource: str
    action: str
    display_name: Optional[str] = None
    description: str
    scope: Scope
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
