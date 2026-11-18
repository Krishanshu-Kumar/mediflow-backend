"""add tender master codes

Revision ID: d2f6a8b0c134
Revises: c1e5f7a9b023
Create Date: 2026-11-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2f6a8b0c134'
down_revision: Union[str, Sequence[str], None] = 'c1e5f7a9b023'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed category 4000 = tender_status and 5000 = tender_item_type."""
    master_codes = sa.table(
        'tb_gl_master_codes',
        sa.column('code', sa.Integer),
        sa.column('category_name', sa.String),
        sa.column('value', sa.String),
        sa.column('display_name', sa.String),
    )
    op.bulk_insert(master_codes, [
        {"code": 4001, "category_name": "tender_status", "value": "draft", "display_name": "Draft"},
        {"code": 4002, "category_name": "tender_status", "value": "published", "display_name": "Published"},
        {"code": 4003, "category_name": "tender_status", "value": "closed", "display_name": "Closed"},
        {"code": 4004, "category_name": "tender_status", "value": "awarded", "display_name": "Awarded"},
        {"code": 4005, "category_name": "tender_status", "value": "cancelled", "display_name": "Cancelled"},
        {"code": 5001, "category_name": "tender_item_type", "value": "medicine", "display_name": "Medicine"},
        {"code": 5002, "category_name": "tender_item_type", "value": "equipment", "display_name": "Equipment"},
    ])


def downgrade() -> None:
    """Remove tender codes."""
    op.execute(
        "DELETE FROM tb_gl_master_codes "
        "WHERE code BETWEEN 4001 AND 4999 OR code BETWEEN 5001 AND 5999"
    )
