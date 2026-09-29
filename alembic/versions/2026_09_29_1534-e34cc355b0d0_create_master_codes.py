"""create master codes

Revision ID: e34cc355b0d0
Revises:
Create Date: 2026-09-29 15:34:34.254244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e34cc355b0d0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    master_codes = op.create_table('tb_gl_master_codes',
    sa.Column('code', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('category_code', sa.Integer(), sa.Computed('(code / 1000) * 1000', persisted=True), nullable=False),
    sa.Column('category_name', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=50), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.CheckConstraint("btrim(display_name) <> ''", name=op.f('ck_tb_gl_master_codes_display_name_not_blank')),
    sa.CheckConstraint("category_name ~ '^[a-z0-9_]+$'", name=op.f('ck_tb_gl_master_codes_category_name_format')),
    sa.CheckConstraint("value ~ '^[a-z0-9_]+$'", name=op.f('ck_tb_gl_master_codes_value_format')),
    sa.CheckConstraint('code > 0 AND mod(code, 1000) <> 0', name=op.f('ck_tb_gl_master_codes_code_not_category')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_tb_gl_master_codes')),
    sa.UniqueConstraint('category_code', 'value', name=op.f('uq_tb_gl_master_codes_category_code_value'))
    )

    # Seed data: category 1000 = tenant plans
    op.bulk_insert(master_codes, [
        {"code": 1001, "category_name": "plan", "value": "free", "display_name": "Free"},
        {"code": 1002, "category_name": "plan", "value": "pro", "display_name": "Pro"},
        {"code": 1003, "category_name": "plan", "value": "enterprise", "display_name": "Enterprise"},
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_master_codes')
