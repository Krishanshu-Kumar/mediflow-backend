"""seed permission display names

Revision ID: f6a2b8d4c075
Revises: e5f1a7c3b964
Create Date: 2026-11-11 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a2b8d4c075'
down_revision: Union[str, Sequence[str], None] = 'e5f1a7c3b964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DISPLAY_NAMES = {
    "tenants.manage": "Manage Hospitals",
    "roles.manage": "Manage Roles",
    "users.manage": "Manage Users",
}


def upgrade() -> None:
    """Upgrade schema."""
    for code, name in DISPLAY_NAMES.items():
        op.execute(
            sa.text("UPDATE tb_gl_permissions SET display_name = :name WHERE code = :code")
            .bindparams(name=name, code=code)
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text("UPDATE tb_gl_permissions SET display_name = NULL WHERE code = ANY(:codes)")
        .bindparams(codes=list(DISPLAY_NAMES))
    )
