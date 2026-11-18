from decimal import Decimal
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

from app.schemas.base import NonNullableUpdateSchema
from app.schemas.Settings.master_codes import MasterCodeResponse

# Trimmed, so a whitespace-only value is rejected here instead of by the DB check
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
ItemName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Unit = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class TenderItemCreate(BaseModel):
    item_type_code: int
    name: ItemName
    specification: Optional[str] = None
    quantity: Decimal = Field(..., gt=0, max_digits=12, decimal_places=3)
    unit: Unit
    notes: Optional[str] = None


class TenderCreate(BaseModel):
    tenant_id: UUID
    title: Title
    description: Optional[str] = None
    # Must include a time zone offset, e.g. 2026-12-01T17:00:00+05:30
    deadline: Optional[AwareDatetime] = None
    items: List[TenderItemCreate] = Field(default_factory=list)


class TenderUpdate(NonNullableUpdateSchema):
    """
    All fields optional for partial updates; only drafts can be updated.
    The tenant cannot be changed. If `items` is sent, it replaces the whole
    item list. Status changes use the /publish, /close and /cancel endpoints.
    """
    non_nullable_fields = ("title", "items")

    title: Optional[Title] = None
    description: Optional[str] = None
    deadline: Optional[AwareDatetime] = None
    items: Optional[List[TenderItemCreate]] = None


class TenderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_no: int
    item_type_code: int
    item_type: MasterCodeResponse
    name: str
    specification: Optional[str] = None
    quantity: float
    unit: str
    notes: Optional[str] = None


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
    deadline: Optional[AwareDatetime] = None
    is_active: bool
    items: List[TenderItemResponse]
