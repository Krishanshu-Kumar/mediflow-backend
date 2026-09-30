import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    """
    created_at / updated_at, both set by the database.
    updated_at is refreshed on every ORM update.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AuditMixin(TimestampMixin):
    """
    Timestamps plus who created / last updated the row.
    Nullable: rows made by migrations or scripts have no acting user.
    """

    # use_alter: users <-> tenants/roles reference each other, so these
    # foreign keys are added after both tables exist
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_auth_users.id", use_alter=True),
    )

    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_auth_users.id", use_alter=True),
    )
