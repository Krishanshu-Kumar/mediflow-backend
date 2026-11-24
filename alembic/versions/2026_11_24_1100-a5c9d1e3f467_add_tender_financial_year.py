"""add financial_year_id to tenders

Revision ID: a5c9d1e3f467
Revises: f4b8c0d2e356
Create Date: 2026-11-24 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5c9d1e3f467'
down_revision: Union[str, Sequence[str], None] = 'f4b8c0d2e356'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. Required column: fails if tenders already exist."""
    op.add_column('tb_tn_tenders', sa.Column('financial_year_id', sa.UUID(), nullable=False))
    op.create_foreign_key(op.f('fk_tb_tn_tenders_financial_year_id_tb_gl_financial_years'), 'tb_tn_tenders', 'tb_gl_financial_years', ['financial_year_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_tb_tn_tenders_financial_year_id_tb_gl_financial_years'), 'tb_tn_tenders', type_='foreignkey')
    op.drop_column('tb_tn_tenders', 'financial_year_id')
