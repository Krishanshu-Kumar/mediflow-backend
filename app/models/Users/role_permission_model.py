import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class RolePermission(Base):
    """
    Grants one permission to one role. A user can do something when their
    role has a row here for the matching permission code.
    """
    __tablename__ = "tb_gl_role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_roles.id"),
        primary_key=True,
    )

    permission_code: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("tb_gl_permissions.code"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
