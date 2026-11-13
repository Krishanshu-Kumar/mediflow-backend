from typing import Any, ClassVar, Tuple

from pydantic import BaseModel, ValidationInfo, field_validator


class NonNullableUpdateSchema(BaseModel):
    """
    Base for partial-update schemas. Fields listed in `non_nullable_fields` may
    be omitted, but cannot be sent as an explicit null (returns a 422 instead of
    a database NOT NULL error).
    """

    non_nullable_fields: ClassVar[Tuple[str, ...]] = ()

    @field_validator("*")
    @classmethod
    def reject_explicit_null(cls, value: Any, info: ValidationInfo) -> Any:
        # Omitted fields never reach this validator (defaults aren't validated),
        # so a None here means the client explicitly sent null.
        if value is None and info.field_name in cls.non_nullable_fields:
            raise ValueError("This field cannot be null")
        return value
