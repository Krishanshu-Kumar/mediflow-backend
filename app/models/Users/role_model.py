from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Role(Base):
    __tablename__ = "tb_gl_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    designation_code = Column(Integer, unique=True, nullable=False)
    designation_group_code = Column(Integer, nullable=False)

    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)

    is_system_role = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True)

    # Temporary: keeping independent while bootstrapping core models
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Uncomment after AuthUser model is created and registered
    # created_by = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("tb_auth_users.id"),
    #     nullable=True,
    # )
    #
    # updated_by = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("tb_auth_users.id"),
    #     nullable=True,
    # )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )