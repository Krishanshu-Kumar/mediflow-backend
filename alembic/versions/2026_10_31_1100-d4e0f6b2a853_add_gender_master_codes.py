"""add gender master codes

Revision ID: d4e0f6b2a853
Revises: c3d9e5a1f742
Create Date: 2026-10-31 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e0f6b2a853'
down_revision: Union[str, Sequence[str], None] = 'c3d9e5a1f742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed category 3000 = gender."""
    master_codes = sa.table(
        'tb_gl_master_codes',
        sa.column('code', sa.Integer),
        sa.column('category_name', sa.String),
        sa.column('value', sa.String),
        sa.column('display_name', sa.String),
    )
    op.bulk_insert(master_codes, [
        {"code": 3001, "category_name": "gender", "value": "male", "display_name": "Male"},
        {"code": 3002, "category_name": "gender", "value": "female", "display_name": "Female"},
        {"code": 3003, "category_name": "gender", "value": "other", "display_name": "Other"},
        {"code": 3004, "category_name": "gender", "value": "unknown", "display_name": "Unknown"},
    ])


def downgrade() -> None:
    """Remove gender codes."""
    op.execute("DELETE FROM tb_gl_master_codes WHERE code BETWEEN 3001 AND 3999")
