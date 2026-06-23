from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class AuthUser(Base):
    __tablename__ = "tb_auth_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_tenants.id"),
        nullable=False,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_roles.id"),
        nullable=False,
    )

    identity_id = Column(UUID(as_uuid=True), nullable=True)

    email = Column(String(255), nullable=False)

    hashed_password = Column(Text, nullable=True)

    full_name = Column(String(255), nullable=False)

    phone = Column(String(20), nullable=True)

    is_active: bool = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    last_login_at = Column(DateTime(timezone=True), nullable=True)

    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

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