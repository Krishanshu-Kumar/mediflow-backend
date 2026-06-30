from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


from sqlalchemy.orm import Mapped

class MasterCode(Base):
    __tablename__ = "tb_gl_master_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    category_code = Column(Integer, nullable=False)
    category_name = Column(String(100), nullable=False)

    code = Column(Integer, unique=True, nullable=False)
    value = Column(String(100), nullable=False)
    display_name = Column(String(150), nullable=False)

    sort_order = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)

    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)  # type: ignore[assignment]
    is_system_code = Column(Boolean, nullable=False, default=False)

    # ForeignKey referencing AuthUser (tb_auth_users)
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

    __table_args__ = (
        UniqueConstraint(
            "category_code", "value", name="uq_tb_gl_master_codes_category_value"
        ),
        CheckConstraint(
            "category_code > 0", name="ck_tb_gl_master_codes_category_code"
        ),
        CheckConstraint("code > 0", name="ck_tb_gl_master_codes_code"),
        CheckConstraint(
            "code >= category_code AND code < (category_code + 1000)",
            name="ck_tb_gl_master_codes_code_in_category",
        ),
    )
