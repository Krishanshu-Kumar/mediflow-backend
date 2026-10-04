# Model registry.
# Alembic imports this package to discover tables: every model that should
# exist in the database must be imported here, or autogenerate won't see it.
from app.models.Settings.master_codes import MasterCode
from app.models.Users.tenant_model import Tenant
from app.models.Users.role_model import Role
from app.models.Users.auth_users_model import AuthUser
from app.models.Users.permission_model import Permission

__all__ = ["MasterCode", "Tenant", "Role", "AuthUser", "Permission"]
