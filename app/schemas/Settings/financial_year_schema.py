from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.schemas.base import NonNullableUpdateSchema

LABEL_PATTERN = r"^20[0-9]{2}-[0-9]{2}$"


class FinancialYearCreate(BaseModel):
    label: str = Field(..., max_length=20, pattern=LABEL_PATTERN, examples=["2026-27"])
    start_date: date
    end_date: date

    @field_validator("label")
    @classmethod
    def check_label_years(cls, value: str) -> str:
        # 2026-27: the part after the dash must be the next year (2099-00 is valid)
        start_year = int(value[:4])
        if int(value[5:]) != (start_year + 1) % 100:
            raise ValueError(f"label must be a consecutive year pair, e.g. {start_year}-{(start_year + 1) % 100:02d}")
        return value

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class FinancialYearUpdate(NonNullableUpdateSchema):
    """
    All fields optional for partial updates.
    Activation is done through the /status endpoint only.
    The label is locked after creation (reference numbers are built from it),
    so it is not updatable.
    If only one date is sent, the other is taken from the stored year, so the
    start < end check for that case happens in the API.
    """
    non_nullable_fields = ("start_date", "end_date")

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class FinancialYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    start_date: date
    end_date: date
    is_active: bool

    @computed_field
    @property
    def is_current(self) -> bool:
        """True if today falls within this financial year's dates."""
        return self.start_date <= date.today() <= self.end_date
