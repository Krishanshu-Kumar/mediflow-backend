from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tb_gl_tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    plan_code = Column(Integer, nullable=False, default=1001)
    is_active = Column(Boolean, default=True)

    settings = Column(JSONB, default=dict)

    created_by = Column(UUID(as_uuid=True), ForeignKey("tb_auth_users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("tb_auth_users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())