"""add status_code to tenders and seed tender_status master codes

Revision ID: c7e1f3a5b689
Revises: b6d0e2f4a578
Create Date: 2026-11-24 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e1f3a5b689'
down_revision: Union[str, Sequence[str], None] = 'b6d0e2f4a578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed category 4000 = tender_status, then add the column (default Draft)."""
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
        {"code": 4004, "category_name": "tender_status", "value": "cancelled", "display_name": "Cancelled"},
    ])

    op.add_column('tb_tn_tenders', sa.Column('status_code', sa.Integer(), server_default='4001', nullable=False))
    op.create_foreign_key(op.f('fk_tb_tn_tenders_status_code_tb_gl_master_codes'), 'tb_tn_tenders', 'tb_gl_master_codes', ['status_code'], ['code'])
    op.create_check_constraint(op.f('ck_tb_tn_tenders_status_code_is_tender_status'), 'tb_tn_tenders', 'status_code BETWEEN 4001 AND 4999')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('ck_tb_tn_tenders_status_code_is_tender_status'), 'tb_tn_tenders', type_='check')
    op.drop_constraint(op.f('fk_tb_tn_tenders_status_code_tb_gl_master_codes'), 'tb_tn_tenders', type_='foreignkey')
    op.drop_column('tb_tn_tenders', 'status_code')
    op.execute("DELETE FROM tb_gl_master_codes WHERE code BETWEEN 4001 AND 4999")
