"""create financial years

Revision ID: b9d4e6f8a012
Revises: a8c3d5e7f901
Create Date: 2026-11-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d4e6f8a012'
down_revision: Union[str, Sequence[str], None] = 'a8c3d5e7f901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tb_gl_financial_years',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('label', sa.String(length=20), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.CheckConstraint("label ~ '^20[0-9]{2}-[0-9]{2}$'", name=op.f('ck_tb_gl_financial_years_label_format')),
    sa.CheckConstraint('start_date < end_date', name=op.f('ck_tb_gl_financial_years_dates_valid')),
    sa.ForeignKeyConstraint(['created_by'], ['tb_auth_users.id'], name=op.f('fk_tb_gl_financial_years_created_by_tb_auth_users'), use_alter=True),
    sa.ForeignKeyConstraint(['updated_by'], ['tb_auth_users.id'], name=op.f('fk_tb_gl_financial_years_updated_by_tb_auth_users'), use_alter=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_gl_financial_years')),
    sa.UniqueConstraint('label', name=op.f('uq_tb_gl_financial_years_label'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_financial_years')
