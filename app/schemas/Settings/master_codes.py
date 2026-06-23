from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class MasterCodeBase(BaseModel):
    category_code: int
    category_name: str = Field(..., max_length=100)

    code: int
    value: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=150)

    sort_order: int = 0
    description: Optional[str] = Field(None)

    is_active: bool = True
    is_system_code: bool = False


class MasterCodeCreate(MasterCodeBase):
    pass


class MasterCodeUpdate(BaseModel):
    """
    All fields optional for partial updates
    """
    category_code: Optional[int] = None
    category_name: Optional[str] = Field(None, max_length=100)

    code: Optional[int] = None
    value: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)

    sort_order: Optional[int] = None
    description: Optional[str] = None

    is_active: Optional[bool] = None
    is_system_code: Optional[bool] = None


class MasterCodeResponse(MasterCodeBase):
    id: UUID

    created_at: datetime
    updated_at: datetime

    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True
