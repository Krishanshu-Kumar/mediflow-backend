"""add financial year audit foreign keys

Revision ID: c1e5f7a9b023
Revises: b9d4e6f8a012
Create Date: 2026-11-17 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c1e5f7a9b023'
down_revision: Union[str, Sequence[str], None] = 'b9d4e6f8a012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # b9d4e6f8a012 passed use_alter inside create_table, which skipped these keys
    op.create_foreign_key(op.f('fk_tb_gl_financial_years_created_by_tb_auth_users'), 'tb_gl_financial_years', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_gl_financial_years_updated_by_tb_auth_users'), 'tb_gl_financial_years', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_tb_gl_financial_years_updated_by_tb_auth_users'), 'tb_gl_financial_years', type_='foreignkey')
    op.drop_constraint(op.f('fk_tb_gl_financial_years_created_by_tb_auth_users'), 'tb_gl_financial_years', type_='foreignkey')
