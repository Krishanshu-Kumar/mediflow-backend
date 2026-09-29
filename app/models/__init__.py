# Model registry.
# Alembic imports this package to discover tables: every model that should
# exist in the database must be imported here, or autogenerate won't see it.
from app.models.Settings.master_codes import MasterCode
from app.models.Users.tenant_model import Tenant

__all__ = ["MasterCode", "Tenant"]
