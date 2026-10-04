"""create permissions

Revision ID: f924f5e30dae
Revises: 98e94ea0e183
Create Date: 2026-10-04 12:30:58.158020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f924f5e30dae'
down_revision: Union[str, Sequence[str], None] = '98e94ea0e183'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    permissions = op.create_table('tb_gl_permissions',
    sa.Column('code', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('scope', sa.String(length=20), nullable=False),
    sa.CheckConstraint("btrim(description) <> ''", name=op.f('ck_tb_gl_permissions_description_not_blank')),
    sa.CheckConstraint("code ~ '^[a-z0-9_]+\\.[a-z0-9_]+$'", name=op.f('ck_tb_gl_permissions_code_format')),
    sa.CheckConstraint("scope IN ('platform', 'tenant')", name=op.f('ck_tb_gl_permissions_scope_valid')),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_tb_gl_permissions'))
    )

    # Seed data: only permissions for features that exist today
    op.bulk_insert(permissions, [
        {"code": "tenants.manage", "description": "Create and manage hospitals (tenants)", "scope": "platform"},
        {"code": "roles.manage", "description": "Create and manage roles", "scope": "tenant"},
        {"code": "users.manage", "description": "Create and manage users", "scope": "tenant"},
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_permissions')
