from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, relationship, foreign
import uuid

from app.core.database import Base
from app.models.base_model import AuditMixin
from app.models.Settings.master_codes import MasterCode


class Tenant(Base, AuditMixin):
    __tablename__ = "tb_gl_tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    plan_code = Column(Integer, nullable=False, default=1001)
    is_active: Mapped[bool] = Column(Boolean, default=True)  # type: ignore[assignment]

    settings = Column(JSONB, default=dict)

    plan_details = relationship(
        "MasterCode",
        primaryjoin="Tenant.plan_code == foreign(MasterCode.code)",
        uselist=False,
        lazy="joined",
    )