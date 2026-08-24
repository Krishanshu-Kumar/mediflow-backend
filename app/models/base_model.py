from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class AuditMixin:
    """
    Mixin class providing standardized audit columns:
    - created_by (UUID, nullable)
    - updated_by (UUID, nullable)
    - created_at (Timestamp with timezone, defaults to DB now)
    - updated_at (Timestamp with timezone, defaults to DB now and auto-updates on edit)
    """

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("tb_auth_users.id"),
        nullable=True,
    )

    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("tb_auth_users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
