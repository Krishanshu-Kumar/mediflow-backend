from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.models.base_model import AuditMixin


from sqlalchemy.orm import Mapped

class Role(Base, AuditMixin):
    __tablename__ = "tb_gl_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    designation_code = Column(Integer, unique=True, nullable=False)
    designation_group_code = Column(Integer, nullable=False)

    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)

    is_system_role: Mapped[bool] = Column(Boolean, default=False)  # type: ignore[assignment]
    is_active: Mapped[bool] = Column(Boolean, default=True)  # type: ignore[assignment]