from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime
import re

# Match the DB check constraint
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(v: str) -> str:
    """Emails are stored lowercase (DB check), so normalize before validating."""
    v = v.strip().lower()
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email format")
    return v


class UserCreate(BaseModel):
    tenant_id: UUID
    role_id: UUID
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt ignores bytes past 72

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return normalize_email(v)


class UserUpdate(BaseModel):
    """
    All fields optional for partial updates.
    Activation is done through the activate/deactivate endpoints only.
    """
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role_id: Optional[UUID] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return normalize_email(v) if v is not None else v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    role_id: UUID
    email: str
    full_name: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]


class UserLogin(BaseModel):
    tenant_slug: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
