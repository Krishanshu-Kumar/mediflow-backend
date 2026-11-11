from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_model import AuditMixin


class Permission(Base, AuditMixin):
    """
    One thing a user may do ("patients.read"). Endpoints check for these codes.
    Rows are managed by Super Admin through the API. A permission only means
    something once endpoint code checks for it, so add the row and the check together.
    """
    __tablename__ = "tb_gl_permissions"

    # "resource.action"; the code itself is the key, so role links can use it directly
    code: Mapped[str] = mapped_column(String(100), primary_key=True)

    description: Mapped[str] = mapped_column(String(255))

    # The two halves of `code`, kept as columns for grouping and filtering
    resource: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50))

    # Friendly label for UIs; falls back to the code when empty
    display_name: Mapped[Optional[str]] = mapped_column(String(100))

    # 'platform' = MediFlow staff only, 'tenant' = a hospital admin may hand it out
    scope: Mapped[str] = mapped_column(String(20))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    __table_args__ = (
        CheckConstraint("code ~ '^[a-z0-9_]+\\.[a-z0-9_]+$'", name="code_format"),
        CheckConstraint("code = resource || '.' || action", name="code_matches_parts"),
        CheckConstraint("btrim(description) <> ''", name="description_not_blank"),
        CheckConstraint("scope IN ('platform', 'tenant')", name="scope_valid"),
    )
