from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime
import re

# Match the DB check constraints
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")


class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = True
    is_verified: bool = False

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not PHONE_REGEX.match(v):
                raise ValueError(
                    "Phone number must be E.164 format: +[country_code][number] (e.g. +1234567890)"
                )
        return v


class UserCreate(UserBase):
    tenant_id: UUID
    role_id: UUID
    identity_id: Optional[UUID] = None
    password: str = Field(..., min_length=6, max_length=255)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[UUID] = None
    identity_id: Optional[UUID] = None
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not PHONE_REGEX.match(v):
                raise ValueError(
                    "Phone number must be E.164 format: +[country_code][number] (e.g. +1234567890)"
                )
        return v


class UserResponse(UserBase):
    id: UUID
    tenant_id: UUID
    role_id: UUID
    identity_id: Optional[UUID]
    last_login_at: Optional[datetime]
    password_changed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    tenant_id: UUID
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
