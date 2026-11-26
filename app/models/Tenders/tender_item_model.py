import uuid
from decimal import Decimal
from enum import IntEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
from app.models.base_model import AuditMixin
from app.models.Settings.master_codes import MasterCode


class TenderItemType(IntEnum):
    """Codes of the tender_item_type category (5000) in tb_gl_master_codes."""
    MEDICINE = 5001
    EQUIPMENT = 5002


class TenderItem(Base, AuditMixin):
    """
    One line of a tender: a medicine or piece of equipment and how much of it
    is needed. Rows are soft-deleted via is_active.
    """
    __tablename__ = "tb_tn_tender_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    tender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_tn_tenders.id"),
        index=True,
    )

    # Line number within the tender, generated (1, 2, 3, ...)
    item_no: Mapped[int] = mapped_column(Integer)

    item_type_code: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tb_gl_master_codes.code"),
    )

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    # Free text, e.g. "strips", "boxes", "nos"
    unit: Mapped[str] = mapped_column(String(50))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    item_type: Mapped[MasterCode] = relationship(lazy="joined")

    __table_args__ = (
        UniqueConstraint("tender_id", "item_no"),
        CheckConstraint("btrim(name) <> ''", name="name_not_blank"),
        CheckConstraint("btrim(unit) <> ''", name="unit_not_blank"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        # Must be a code from the TENDER_ITEM_TYPE category (5000)
        CheckConstraint("item_type_code BETWEEN 5001 AND 5999", name="item_type_code_is_tender_item_type"),
    )
