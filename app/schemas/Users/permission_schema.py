from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Scope = Literal["platform", "tenant"]


class PermissionCreate(BaseModel):
    # "resource.action"; same format the database enforces
    code: str = Field(..., max_length=100, pattern=r"^[a-z0-9_]+\.[a-z0-9_]+$")
    description: str = Field(..., min_length=1, max_length=255)
    scope: Scope


class PermissionUpdate(BaseModel):
    """The code is the key that roles and endpoints refer to, so it can't change."""
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    scope: Optional[Scope] = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    description: str
    scope: Scope
