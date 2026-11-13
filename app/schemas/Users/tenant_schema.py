from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import NonNullableUpdateSchema
from app.schemas.Settings.master_codes import MasterCodeResponse

SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., max_length=100, pattern=SLUG_PATTERN)
    plan_code: int = 1001


class TenantUpdate(NonNullableUpdateSchema):
    """
    All fields optional for partial updates.
    Activation is done through the /status endpoint only.
    The slug is locked after creation (it is what users type to log in), so it
    is not updatable.
    """
    non_nullable_fields = ("name", "plan_code")

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    plan_code: Optional[int] = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    plan_code: int
    plan: MasterCodeResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime
