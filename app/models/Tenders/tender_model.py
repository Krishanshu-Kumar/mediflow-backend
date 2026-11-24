import uuid
from datetime import datetime
from enum import IntEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base_model import AuditMixin
from app.models.Settings.master_codes import MasterCode


class TenderStatus(IntEnum):
    """Codes of the tender_status category (4000) in tb_gl_master_codes."""
    DRAFT = 4001
    PUBLISHED = 4002
    CLOSED = 4003
    CANCELLED = 4004


class Tender(Base, AuditMixin):
    """
    A request raised by a tenant (hospital) for medicine or equipment.
    What is needed is written in the description. Rows are soft-deleted via is_active.
    """
    __tablename__ = "tb_tn_tenders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_tenants.id"),
        index=True,
    )

    # The financial year the tender was created in (global, not per tenant)
    financial_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_gl_financial_years.id"),
    )

    # e.g. TND-2026-27-0001, unique within the tenant
    reference_no: Mapped[str] = mapped_column(String(50))

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    status_code: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tb_gl_master_codes.code"),
        default=TenderStatus.DRAFT,
        server_default=str(int(TenderStatus.DRAFT)),
    )

    # Both optional and informational for now
    pre_bid_meeting_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    status: Mapped[MasterCode] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("tenant_id", "reference_no"),
        CheckConstraint("btrim(title) <> ''", name="title_not_blank"),
        # Must be a code from the TENDER_STATUS category (4000)
        CheckConstraint("status_code BETWEEN 4001 AND 4999", name="status_code_is_tender_status"),
    )
