"""add payment status master codes

Revision ID: c3d9e5a1f742
Revises: a7c41d9e2b68
Create Date: 2026-10-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d9e5a1f742'
down_revision: Union[str, Sequence[str], None] = 'a7c41d9e2b68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed category 2000 = payment status."""
    master_codes = sa.table(
        'tb_gl_master_codes',
        sa.column('code', sa.Integer),
        sa.column('category_name', sa.String),
        sa.column('value', sa.String),
        sa.column('display_name', sa.String),
    )
    op.bulk_insert(master_codes, [
        {"code": 2001, "category_name": "payment_status", "value": "pending", "display_name": "Pending"},
        {"code": 2002, "category_name": "payment_status", "value": "paid", "display_name": "Paid"},
        {"code": 2003, "category_name": "payment_status", "value": "partial", "display_name": "Partially Paid"},
        {"code": 2004, "category_name": "payment_status", "value": "refunded", "display_name": "Refunded"},
    ])


def downgrade() -> None:
    """Remove payment status codes."""
    op.execute("DELETE FROM tb_gl_master_codes WHERE code BETWEEN 2001 AND 2999")
