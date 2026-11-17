import uuid
from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base_model import AuditMixin


class FinancialYear(Base, AuditMixin):
    """
    A financial year (e.g. 2026-27). Global: shared by all tenants.
    Date ranges must not overlap; that is enforced in the CRUD layer.
    """
    __tablename__ = "tb_gl_financial_years"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    label: Mapped[str] = mapped_column(String(20), unique=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    __table_args__ = (
        CheckConstraint("label ~ '^20[0-9]{2}-[0-9]{2}$'", name="label_format"),
        CheckConstraint("start_date < end_date", name="dates_valid"),
    )
