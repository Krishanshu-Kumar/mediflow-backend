"""create users

Revision ID: 98e94ea0e183
Revises: b5680d19cf57
Create Date: 2026-09-30 15:21:27.336935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98e94ea0e183'
down_revision: Union[str, Sequence[str], None] = 'b5680d19cf57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Must exist before the users (tenant_id, role_id) foreign key that points at it
    op.create_unique_constraint(op.f('uq_tb_gl_roles_tenant_id_id'), 'tb_gl_roles', ['tenant_id', 'id'])

    op.create_table('tb_auth_users',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.Text(), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(full_name) <> ''", name=op.f('ck_tb_auth_users_full_name_not_blank')),
    sa.CheckConstraint("email ~ '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'", name=op.f('ck_tb_auth_users_email_format')),
    sa.CheckConstraint('email = lower(email)', name=op.f('ck_tb_auth_users_email_lowercase')),
    sa.ForeignKeyConstraint(['tenant_id', 'role_id'], ['tb_gl_roles.tenant_id', 'tb_gl_roles.id'], name='fk_tb_auth_users_role_in_tenant'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tb_gl_tenants.id'], name=op.f('fk_tb_auth_users_tenant_id_tb_gl_tenants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tb_auth_users')),
    sa.UniqueConstraint('tenant_id', 'email', name=op.f('uq_tb_auth_users_tenant_id_email'))
    )
    # Self-references: added after the table exists (create_table skips use_alter FKs)
    op.create_foreign_key(op.f('fk_tb_auth_users_created_by_tb_auth_users'), 'tb_auth_users', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_auth_users_updated_by_tb_auth_users'), 'tb_auth_users', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)

    # Audit columns on tables created before users existed
    op.add_column('tb_gl_roles', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('tb_gl_roles', sa.Column('updated_by', sa.UUID(), nullable=True))
    op.create_foreign_key(op.f('fk_tb_gl_roles_created_by_tb_auth_users'), 'tb_gl_roles', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_gl_roles_updated_by_tb_auth_users'), 'tb_gl_roles', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)
    op.add_column('tb_gl_tenants', sa.Column('created_by', sa.UUID(), nullable=True))
    op.add_column('tb_gl_tenants', sa.Column('updated_by', sa.UUID(), nullable=True))
    op.create_foreign_key(op.f('fk_tb_gl_tenants_created_by_tb_auth_users'), 'tb_gl_tenants', 'tb_auth_users', ['created_by'], ['id'], use_alter=True)
    op.create_foreign_key(op.f('fk_tb_gl_tenants_updated_by_tb_auth_users'), 'tb_gl_tenants', 'tb_auth_users', ['updated_by'], ['id'], use_alter=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_tb_gl_tenants_updated_by_tb_auth_users'), 'tb_gl_tenants', type_='foreignkey')
    op.drop_constraint(op.f('fk_tb_gl_tenants_created_by_tb_auth_users'), 'tb_gl_tenants', type_='foreignkey')
    op.drop_column('tb_gl_tenants', 'updated_by')
    op.drop_column('tb_gl_tenants', 'created_by')
    op.drop_constraint(op.f('fk_tb_gl_roles_updated_by_tb_auth_users'), 'tb_gl_roles', type_='foreignkey')
    op.drop_constraint(op.f('fk_tb_gl_roles_created_by_tb_auth_users'), 'tb_gl_roles', type_='foreignkey')
    op.drop_column('tb_gl_roles', 'updated_by')
    op.drop_column('tb_gl_roles', 'created_by')
    op.drop_table('tb_auth_users')
    op.drop_constraint(op.f('uq_tb_gl_roles_tenant_id_id'), 'tb_gl_roles', type_='unique')
