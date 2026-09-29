from enum import IntEnum

from sqlalchemy import Boolean, CheckConstraint, Computed, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MasterCodeCategory(IntEnum):
    """
    Each category owns a block of 1000 codes: category 1000 owns 1001-1999.
    Add a category here only when a feature starts using it.
    """
    PLAN = 1000


class MasterCode(Base):
    """
    Global lookup values (plans, statuses, ...), referenced by other tables
    through `code`. Rows are managed by migrations, not by the API.
    """
    __tablename__ = "tb_gl_master_codes"

    code: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    # Derived by Postgres from `code` (4007 -> 4000), so it can never disagree with it.
    # Category lookups use the (category_code, value) unique index below.
    category_code: Mapped[int] = mapped_column(
        Integer,
        Computed("(code / 1000) * 1000", persisted=True),
    )

    value: Mapped[str] = mapped_column(String(50))
    display_name: Mapped[str] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    __table_args__ = (
        UniqueConstraint("category_code", "value"),
        # X000 is the category itself, not a usable code
        CheckConstraint("code > 0 AND mod(code, 1000) <> 0", name="code_not_category"),
        CheckConstraint("value ~ '^[a-z0-9_]+$'", name="value_format"),
        CheckConstraint("btrim(display_name) <> ''", name="display_name_not_blank"),
    )
