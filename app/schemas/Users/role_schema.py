from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    designation_code: int
    designation_group_code: int

    name: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=100)

    is_system_role: bool = False
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    """
    All fields optional for partial updates
    """
    designation_code: Optional[int] = None
    designation_group_code: Optional[int] = None

    name: Optional[str] = Field(None, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)

    is_system_role: Optional[bool] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: UUID

    created_at: datetime
    updated_at: datetime

    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True