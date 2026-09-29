"""create tenants

Revision ID: 3e1faf2bb21a
Revises: e34cc355b0d0
Create Date: 2026-09-29 15:52:26.674160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid import UUID


# revision identifiers, used by Alembic.
revision: str = '3e1faf2bb21a'
down_revision: Union[str, Sequence[str], None] = 'e34cc355b0d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hardcoded on purpose: migrations must not change if app code changes later
SYSTEM_TENANT_ID = UUID("cec393c8-9c66-444c-83a7-6f6c941b5153")


def upgrade() -> None:
    """Upgrade schema."""
    tenants = op.create_table('tb_gl_tenants',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('plan_code', sa.Integer(), server_default='1001', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(name) <> ''", name=op.f('ck_tb_gl_tenants_name_not_blank')),
    sa.CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name=op.f('ck_tb_gl_tenants_slug_format')),
    sa.CheckConstraint('plan_code BETWEEN 1001 AND 1999', name=op.f('ck_tb_gl_tenants_plan_code_is_plan')),
    sa.ForeignKeyConstraint(['plan_code'], ['tb_gl_master_codes.code'], name=op.f('fk_tb_gl_tenants_plan_code_tb_gl_master_codes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_gl_tenants')),
    sa.UniqueConstraint('slug', name=op.f('uq_tb_gl_tenants_slug'))
    )

    # Seed data: the MediFlow platform tenant (id must match app.core.constants.SYSTEM_TENANT_ID)
    op.bulk_insert(tenants, [
        {"id": SYSTEM_TENANT_ID, "name": "MediFlow", "slug": "mediflow", "plan_code": 1003},
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_tenants')
