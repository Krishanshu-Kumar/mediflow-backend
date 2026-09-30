import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_model import AuditMixin


class AuthUser(Base, AuditMixin):
    """
    A person who can log in. Belongs to exactly one tenant and holds one of
    that tenant's roles. The same email may exist once in each tenant.
    """
    __tablename__ = "tb_auth_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_tenants.id"),
    )
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    # Always stored lowercase, so "A@x.com" and "a@x.com" are the same account
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # The role must belong to the user's own tenant, not just exist
        ForeignKeyConstraint(
            ["tenant_id", "role_id"],
            ["tb_gl_roles.tenant_id", "tb_gl_roles.id"],
            name="fk_tb_auth_users_role_in_tenant",
        ),
        UniqueConstraint("tenant_id", "email"),
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint(r"email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$'", name="email_format"),
        CheckConstraint("btrim(full_name) <> ''", name="full_name_not_blank"),
    )
