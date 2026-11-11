"""add permission columns

Revision ID: e5f1a7c3b964
Revises: d4e0f6b2a853
Create Date: 2026-11-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f1a7c3b964'
down_revision: Union[str, Sequence[str], None] = 'd4e0f6b2a853'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # resource/action are added nullable, backfilled from code, then made required
    op.add_column('tb_gl_permissions', sa.Column('resource', sa.String(length=50), nullable=True))
    op.add_column('tb_gl_permissions', sa.Column('action', sa.String(length=50), nullable=True))
    op.execute("UPDATE tb_gl_permissions SET resource = split_part(code, '.', 1), action = split_part(code, '.', 2)")
    op.alter_column('tb_gl_permissions', 'resource', nullable=False)
    op.alter_column('tb_gl_permissions', 'action', nullable=False)

    op.add_column('tb_gl_permissions', sa.Column('display_name', sa.String(length=100), nullable=True))
    op.add_column('tb_gl_permissions', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('tb_gl_permissions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tb_gl_permissions', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tb_gl_permissions', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('tb_gl_permissions', sa.Column('updated_by', sa.UUID(), nullable=True))

    op.create_check_constraint(
        op.f('ck_tb_gl_permissions_code_matches_parts'),
        'tb_gl_permissions',
        "code = resource || '.' || action",
    )
    op.create_foreign_key(op.f('fk_tb_gl_permissions_created_by_tb_auth_users'), 'tb_gl_permissions', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_gl_permissions_updated_by_tb_auth_users'), 'tb_gl_permissions', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_tb_gl_permissions_updated_by_tb_auth_users'), 'tb_gl_permissions', type_='foreignkey')
    op.drop_constraint(op.f('fk_tb_gl_permissions_created_by_tb_auth_users'), 'tb_gl_permissions', type_='foreignkey')
    op.drop_constraint(op.f('ck_tb_gl_permissions_code_matches_parts'), 'tb_gl_permissions', type_='check')
    op.drop_column('tb_gl_permissions', 'updated_by')
    op.drop_column('tb_gl_permissions', 'created_by')
    op.drop_column('tb_gl_permissions', 'updated_at')
    op.drop_column('tb_gl_permissions', 'created_at')
    op.drop_column('tb_gl_permissions', 'is_active')
    op.drop_column('tb_gl_permissions', 'display_name')
    op.drop_column('tb_gl_permissions', 'action')
    op.drop_column('tb_gl_permissions', 'resource')
