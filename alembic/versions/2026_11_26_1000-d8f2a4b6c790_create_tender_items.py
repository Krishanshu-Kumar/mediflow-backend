"""create tender items and seed tender_item_type master codes

Revision ID: d8f2a4b6c790
Revises: c7e1f3a5b689
Create Date: 2026-11-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8f2a4b6c790'
down_revision: Union[str, Sequence[str], None] = 'c7e1f3a5b689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed category 5000 = tender_item_type, then create the items table."""
    master_codes = sa.table(
        'tb_gl_master_codes',
        sa.column('code', sa.Integer),
        sa.column('category_name', sa.String),
        sa.column('value', sa.String),
        sa.column('display_name', sa.String),
    )
    op.bulk_insert(master_codes, [
        {"code": 5001, "category_name": "tender_item_type", "value": "medicine", "display_name": "Medicine"},
        {"code": 5002, "category_name": "tender_item_type", "value": "equipment", "display_name": "Equipment"},
    ])

    op.create_table('tb_tn_tender_items',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tender_id', sa.UUID(), nullable=False),
    sa.Column('item_no', sa.Integer(), nullable=False),
    sa.Column('item_type_code', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.CheckConstraint("btrim(name) <> ''", name=op.f('ck_tb_tn_tender_items_name_not_blank')),
    sa.CheckConstraint("btrim(unit) <> ''", name=op.f('ck_tb_tn_tender_items_unit_not_blank')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_tb_tn_tender_items_quantity_positive')),
    sa.CheckConstraint('item_type_code BETWEEN 5001 AND 5999', name=op.f('ck_tb_tn_tender_items_item_type_code_is_tender_item_type')),
    sa.ForeignKeyConstraint(['tender_id'], ['tb_tn_tenders.id'], name=op.f('fk_tb_tn_tender_items_tender_id_tb_tn_tenders')),
    sa.ForeignKeyConstraint(['item_type_code'], ['tb_gl_master_codes.code'], name=op.f('fk_tb_tn_tender_items_item_type_code_tb_gl_master_codes')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_tn_tender_items')),
    sa.UniqueConstraint('tender_id', 'item_no', name=op.f('uq_tb_tn_tender_items_tender_id_item_no'))
    )
    op.create_index(op.f('ix_tb_tn_tender_items_tender_id'), 'tb_tn_tender_items', ['tender_id'], unique=False)
    # Added separately: create_table skips use_alter foreign keys
    op.create_foreign_key(op.f('fk_tb_tn_tender_items_created_by_tb_auth_users'), 'tb_tn_tender_items', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_tn_tender_items_updated_by_tb_auth_users'), 'tb_tn_tender_items', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)


def downgrade() -> None:
    """Drop the items table and the item type codes."""
    op.drop_table('tb_tn_tender_items')
    op.execute("DELETE FROM tb_gl_master_codes WHERE code BETWEEN 5001 AND 5999")
