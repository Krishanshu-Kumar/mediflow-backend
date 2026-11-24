from typing import Annotated, Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, StringConstraints

from app.schemas.base import NonNullableUpdateSchema
from app.schemas.Settings.master_codes import MasterCodeResponse

# Trimmed, so a whitespace-only value is rejected here instead of by the DB check
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class TenderCreate(BaseModel):
    tenant_id: UUID
    title: Title
    description: Optional[str] = None
    # Both must include a time zone offset, e.g. 2026-12-01T17:00:00+05:30
    pre_bid_meeting_at: Optional[AwareDatetime] = None
    deadline: Optional[AwareDatetime] = None


class TenderUpdate(NonNullableUpdateSchema):
    """All fields optional for partial updates. The tenant cannot be changed."""
    non_nullable_fields = ("title", "status_code")

    title: Optional[Title] = None
    # Must be a code from the tender_status category (4001-4004)
    status_code: Optional[int] = None
    description: Optional[str] = None
    pre_bid_meeting_at: Optional[AwareDatetime] = None
    deadline: Optional[AwareDatetime] = None


class TenderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    financial_year_id: UUID
    reference_no: str
    title: str
    description: Optional[str] = None
    status_code: int
    status: MasterCodeResponse
    pre_bid_meeting_at: Optional[AwareDatetime] = None
    deadline: Optional[AwareDatetime] = None
    is_active: bool
