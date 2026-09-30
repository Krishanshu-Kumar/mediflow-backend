import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_model import AuditMixin


class Role(Base, AuditMixin):
    """
    A job role inside one tenant ("Nurse", "Receptionist").
    Each tenant names its own roles; platform roles live in the MediFlow tenant.
    """
    __tablename__ = "tb_gl_roles"

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

    name: Mapped[str] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    __table_args__ = (
        # Two hospitals can both have a "Nurse" role, but not two inside one hospital
        UniqueConstraint("tenant_id", "name"),
        # Target of the users (tenant_id, role_id) foreign key, which guarantees
        # a user's role belongs to the user's own tenant
        UniqueConstraint("tenant_id", "id"),
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
    )
