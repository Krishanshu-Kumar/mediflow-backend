import uuid
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base_model import AuditMixin, TimestampMixin
from app.models.Settings.master_codes import MasterCode


class TenderStatus(IntEnum):
    """Codes of the tender_status category (4000) in tb_gl_master_codes."""
    DRAFT = 4001
    PUBLISHED = 4002
    CLOSED = 4003
    AWARDED = 4004
    CANCELLED = 4005


class Tender(Base, AuditMixin):
    """
    A request raised by a tenant (hospital) for medicine or equipment.
    The requirements are its line items. Rows are soft-deleted via is_active.
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

    # Last moment offers are accepted. Optional in draft, required to publish
    # (enforced in the API, not here).
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    status: Mapped[MasterCode] = relationship(lazy="joined")
    items: Mapped[List["TenderItem"]] = relationship(
        back_populates="tender",
        cascade="all, delete-orphan",
        order_by="TenderItem.line_no",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "reference_no"),
        CheckConstraint("btrim(title) <> ''", name="title_not_blank"),
        # Must be a code from the TENDER_STATUS category (4000)
        CheckConstraint("status_code BETWEEN 4001 AND 4999", name="status_code_is_tender_status"),
    )


class TenderItem(Base, TimestampMixin):
    """One requirement of a tender, e.g. 'Paracetamol 500mg, 10000 strips'."""
    __tablename__ = "tb_tn_tender_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    tender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_tn_tenders.id", ondelete="CASCADE"),
        index=True,
    )

    # 1-based position in the tender, keeps the order the client sent
    line_no: Mapped[int] = mapped_column(Integer)

    item_type_code: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tb_gl_master_codes.code"),
    )

    name: Mapped[str] = mapped_column(String(255))
    specification: Mapped[Optional[str]] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    unit: Mapped[str] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    tender: Mapped[Tender] = relationship(back_populates="items")
    item_type: Mapped[MasterCode] = relationship(lazy="joined")

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
        CheckConstraint("btrim(unit) <> ''", name="unit_not_blank"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        # Must be a code from the TENDER_ITEM_TYPE category (5000)
        CheckConstraint("item_type_code BETWEEN 5001 AND 5999", name="item_type_code_is_item_type"),
    )
