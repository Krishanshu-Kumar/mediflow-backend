"""create role permissions

Revision ID: a7c41d9e2b68
Revises: f924f5e30dae
Create Date: 2026-10-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c41d9e2b68'
down_revision: Union[str, Sequence[str], None] = 'f924f5e30dae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tb_gl_role_permissions',
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_code', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['permission_code'], ['tb_gl_permissions.code'], name=op.f('fk_tb_gl_role_permissions_permission_code_tb_gl_permissions')),
    sa.ForeignKeyConstraint(['role_id'], ['tb_gl_roles.id'], name=op.f('fk_tb_gl_role_permissions_role_id_tb_gl_roles')),
    sa.PrimaryKeyConstraint('role_id', 'permission_code', name=op.f('pk_tb_gl_role_permissions'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_gl_role_permissions')
