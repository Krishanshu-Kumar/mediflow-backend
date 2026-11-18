"""create tenders

Revision ID: e3a7b9c1d245
Revises: d2f6a8b0c134
Create Date: 2026-11-18 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3a7b9c1d245'
down_revision: Union[str, Sequence[str], None] = 'd2f6a8b0c134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tb_tn_tenders',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('financial_year_id', sa.UUID(), nullable=False),
    sa.Column('reference_no', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status_code', sa.Integer(), server_default='4001', nullable=False),
    sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.CheckConstraint("btrim(title) <> ''", name=op.f('ck_tb_tn_tenders_title_not_blank')),
    sa.CheckConstraint('status_code BETWEEN 4001 AND 4999', name=op.f('ck_tb_tn_tenders_status_code_is_tender_status')),
    sa.ForeignKeyConstraint(['tenant_id'], ['tb_gl_tenants.id'], name=op.f('fk_tb_tn_tenders_tenant_id_tb_gl_tenants')),
    sa.ForeignKeyConstraint(['financial_year_id'], ['tb_gl_financial_years.id'], name=op.f('fk_tb_tn_tenders_financial_year_id_tb_gl_financial_years')),
    sa.ForeignKeyConstraint(['status_code'], ['tb_gl_master_codes.code'], name=op.f('fk_tb_tn_tenders_status_code_tb_gl_master_codes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_tn_tenders')),
    sa.UniqueConstraint('tenant_id', 'reference_no', name=op.f('uq_tb_tn_tenders_tenant_id_reference_no'))
    )
    op.create_index(op.f('ix_tb_tn_tenders_tenant_id'), 'tb_tn_tenders', ['tenant_id'], unique=False)
    # Added separately: create_table skips use_alter foreign keys
    op.create_foreign_key(op.f('fk_tb_tn_tenders_created_by_tb_auth_users'), 'tb_tn_tenders', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_tn_tenders_updated_by_tb_auth_users'), 'tb_tn_tenders', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)

    op.create_table('tb_tn_tender_items',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tender_id', sa.UUID(), nullable=False),
    sa.Column('line_no', sa.Integer(), nullable=False),
    sa.Column('item_type_code', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('specification', sa.Text(), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(name) <> ''", name=op.f('ck_tb_tn_tender_items_name_not_blank')),
    sa.CheckConstraint("btrim(unit) <> ''", name=op.f('ck_tb_tn_tender_items_unit_not_blank')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_tb_tn_tender_items_quantity_positive')),
    sa.CheckConstraint('item_type_code BETWEEN 5001 AND 5999', name=op.f('ck_tb_tn_tender_items_item_type_code_is_item_type')),
    sa.ForeignKeyConstraint(['tender_id'], ['tb_tn_tenders.id'], name=op.f('fk_tb_tn_tender_items_tender_id_tb_tn_tenders'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['item_type_code'], ['tb_gl_master_codes.code'], name=op.f('fk_tb_tn_tender_items_item_type_code_tb_gl_master_codes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_tn_tender_items'))
    )
    op.create_index(op.f('ix_tb_tn_tender_items_tender_id'), 'tb_tn_tender_items', ['tender_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tb_tn_tender_items')
    op.drop_table('tb_tn_tenders')
