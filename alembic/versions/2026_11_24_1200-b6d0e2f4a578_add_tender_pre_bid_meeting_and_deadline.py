"""add pre_bid_meeting_at and deadline to tenders

Revision ID: b6d0e2f4a578
Revises: a5c9d1e3f467
Create Date: 2026-11-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6d0e2f4a578'
down_revision: Union[str, Sequence[str], None] = 'a5c9d1e3f467'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tb_tn_tenders', sa.Column('pre_bid_meeting_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tb_tn_tenders', sa.Column('deadline', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tb_tn_tenders', 'deadline')
    op.drop_column('tb_tn_tenders', 'pre_bid_meeting_at')
