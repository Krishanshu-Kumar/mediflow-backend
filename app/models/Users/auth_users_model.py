from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from typing import Optional

from app.core.database import Base

from sqlalchemy.orm import Mapped

class AuthUser(Base):
    __tablename__ = "tb_auth_users"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # type: ignore[assignment]

    tenant_id: Mapped[uuid.UUID] = Column(  # type: ignore[assignment]
        UUID(as_uuid=True),
        ForeignKey("tb_gl_tenants.id"),
        nullable=False,
    )

    role_id: Mapped[uuid.UUID] = Column(  # type: ignore[assignment]
        UUID(as_uuid=True),
        ForeignKey("tb_gl_roles.id"),
        nullable=False,
    )

    identity_id: Mapped[Optional[uuid.UUID]] = Column(UUID(as_uuid=True), nullable=True)  # type: ignore[assignment]

    email: Mapped[str] = Column(String(255), nullable=False)  # type: ignore[assignment]

    hashed_password: Mapped[Optional[str]] = Column(Text, nullable=True)  # type: ignore[assignment]

    full_name: Mapped[str] = Column(String(255), nullable=False)  # type: ignore[assignment]

    phone: Mapped[Optional[str]] = Column(String(20), nullable=True)  # type: ignore[assignment]

    is_active: Mapped[bool] = Column(Boolean, default=True)  # type: ignore[assignment]
    is_verified: Mapped[bool] = Column(Boolean, default=False)  # type: ignore[assignment]

    last_login_at: Mapped[Optional[DateTime]] = Column(DateTime(timezone=True), nullable=True)  # type: ignore[assignment]

    password_changed_at: Mapped[Optional[DateTime]] = Column(  # type: ignore[assignment]
        DateTime(timezone=True),
        nullable=True,
    )

    created_by: Mapped[Optional[uuid.UUID]] = Column(  # type: ignore[assignment]
        UUID(as_uuid=True),
        ForeignKey("tb_auth_users.id"),
        nullable=True,
    )

    updated_by: Mapped[Optional[uuid.UUID]] = Column(  # type: ignore[assignment]
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