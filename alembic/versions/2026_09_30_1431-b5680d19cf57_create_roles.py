"""create roles

Revision ID: b5680d19cf57
Revises: 3e1faf2bb21a
Create Date: 2026-09-30 14:31:04.015532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid import UUID


# revision identifiers, used by Alembic.
revision: str = 'b5680d19cf57'
down_revision: Union[str, Sequence[str], None] = '3e1faf2bb21a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Hardcoded on purpose: migrations must not change if app code changes later
SYSTEM_TENANT_ID = UUID("cec393c8-9c66-444c-83a7-6f6c941b5153")
SUPER_ADMIN_ROLE_ID = UUID("5b0e2f7a-3c1d-4e8b-9a6f-2d4c8e1b7a93")


def upgrade() -> None:
    """Upgrade schema."""
    roles = op.create_table('tb_gl_roles',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(name) <> ''", name=op.f('ck_tb_gl_roles_name_not_blank')),
    sa.ForeignKeyConstraint(['tenant_id'], ['tb_gl_tenants.id'], name=op.f('fk_tb_gl_roles_tenant_id_tb_gl_tenants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_gl_roles')),
    sa.UniqueConstraint('tenant_id', 'name', name=op.f('uq_tb_gl_roles_tenant_id_name'))
    )

    # Seed data: the platform Super Admin role (id must match app.core.constants.SUPER_ADMIN_ROLE_ID)
    op.bulk_insert(roles, [
        {"id": SUPER_ADMIN_ROLE_ID, "tenant_id": SYSTEM_TENANT_ID, "name": "Super Admin"},
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_roles')
