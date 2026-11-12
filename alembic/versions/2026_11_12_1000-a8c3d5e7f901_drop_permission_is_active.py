"""drop is_active from permissions

Revision ID: a8c3d5e7f901
Revises: f6a2b8d4c075
Create Date: 2026-11-12 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8c3d5e7f901'
down_revision: Union[str, Sequence[str], None] = 'f6a2b8d4c075'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('tb_gl_permissions', 'is_active')


def downgrade() -> None:
    op.add_column('tb_gl_permissions', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
