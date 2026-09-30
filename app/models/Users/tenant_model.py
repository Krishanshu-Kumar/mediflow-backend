import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base_model import AuditMixin
from app.models.Settings.master_codes import MasterCode


class Tenant(Base, AuditMixin):
    """
    An organization (hospital, clinic) using MediFlow. Root of all tenant data.
    """
    __tablename__ = "tb_gl_tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True)

    plan_code: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tb_gl_master_codes.code"),
        server_default="1001",
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    plan: Mapped[MasterCode] = relationship(lazy="joined")

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
        CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="slug_format"),
        # Must be a code from the PLAN category (1000)
        CheckConstraint("plan_code BETWEEN 1001 AND 1999", name="plan_code_is_plan"),
    )
