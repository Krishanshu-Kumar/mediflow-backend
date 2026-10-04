from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Permission(Base):
    """
    One thing a user may do ("patients.read"). Endpoints check for these codes.
    Rows are managed by migrations, not by the API: a permission only means
    something once code checks for it, so both ship together.
    """
    __tablename__ = "tb_gl_permissions"

    # "resource.action"; the code itself is the key, so role links can use it directly
    code: Mapped[str] = mapped_column(String(100), primary_key=True)

    description: Mapped[str] = mapped_column(String(255))

    # 'platform' = MediFlow staff only, 'tenant' = a hospital admin may hand it out
    scope: Mapped[str] = mapped_column(String(20))

    __table_args__ = (
        CheckConstraint("code ~ '^[a-z0-9_]+\\.[a-z0-9_]+$'", name="code_format"),
        CheckConstraint("btrim(description) <> ''", name="description_not_blank"),
        CheckConstraint("scope IN ('platform', 'tenant')", name="scope_valid"),
    )
