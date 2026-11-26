from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.schemas.base import NonNullableUpdateSchema
from app.schemas.Settings.master_codes import MasterCodeResponse

# Trimmed, so a whitespace-only value is rejected here instead of by the DB check
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Unit = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Quantity = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=3)]


class TenderItemCreate(BaseModel):
    # Must be a code from the tender_item_type category (5001 medicine, 5002 equipment)
    item_type_code: int
    name: Name
    description: Optional[str] = None
    quantity: Quantity
    unit: Unit


class TenderItemUpdate(NonNullableUpdateSchema):
    """All fields optional for partial updates."""
    non_nullable_fields = ("item_type_code", "name", "quantity", "unit")

    item_type_code: Optional[int] = None
    name: Optional[Name] = None
    description: Optional[str] = None
    quantity: Optional[Quantity] = None
    unit: Optional[Unit] = None


class TenderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID
    item_no: int
    item_type_code: int
    item_type: MasterCodeResponse
    name: str
    description: Optional[str] = None
    quantity: Decimal
    unit: str
    is_active: bool
