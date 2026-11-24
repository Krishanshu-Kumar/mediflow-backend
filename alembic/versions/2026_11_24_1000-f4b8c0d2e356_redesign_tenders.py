"""redesign tenders as a single basic table

Revision ID: f4b8c0d2e356
Revises: e3a7b9c1d245
Create Date: 2026-11-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4b8c0d2e356'
down_revision: Union[str, Sequence[str], None] = 'e3a7b9c1d245'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the old tender tables (and their data) and create the basic one."""
    op.drop_table('tb_tn_tender_items')
    op.drop_table('tb_tn_tenders')
    op.execute(
        "DELETE FROM tb_gl_master_codes "
        "WHERE code BETWEEN 4001 AND 4999 OR code BETWEEN 5001 AND 5999"
    )

    op.create_table('tb_tn_tenders',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('reference_no', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.CheckConstraint("btrim(title) <> ''", name=op.f('ck_tb_tn_tenders_title_not_blank')),
    sa.ForeignKeyConstraint(['tenant_id'], ['tb_gl_tenants.id'], name=op.f('fk_tb_tn_tenders_tenant_id_tb_gl_tenants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_tn_tenders')),
    sa.UniqueConstraint('tenant_id', 'reference_no', name=op.f('uq_tb_tn_tenders_tenant_id_reference_no'))
    )
    op.create_index(op.f('ix_tb_tn_tenders_tenant_id'), 'tb_tn_tenders', ['tenant_id'], unique=False)
    # Added separately: create_table skips use_alter foreign keys
    op.create_foreign_key(op.f('fk_tb_tn_tenders_created_by_tb_auth_users'), 'tb_tn_tenders', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_tn_tenders_updated_by_tb_auth_users'), 'tb_tn_tenders', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)


def downgrade() -> None:
    """The dropped tables and their data cannot be restored."""
    raise NotImplementedError("Irreversible: the old tender tables and their data were dropped")
