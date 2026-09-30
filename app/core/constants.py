from uuid import UUID

# The MediFlow platform's own tenant. Created by the "create tenants" migration
# with this fixed id, and protected from modification through the API.
SYSTEM_TENANT_ID = UUID("cec393c8-9c66-444c-83a7-6f6c941b5153")

# The platform Super Admin role, inside the system tenant. Created by the
# "create roles" migration with this fixed id, and protected like the tenant.
SUPER_ADMIN_ROLE_ID = UUID("5b0e2f7a-3c1d-4e8b-9a6f-2d4c8e1b7a93")
