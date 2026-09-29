from uuid import UUID

# The MediFlow platform's own tenant. Created by the "create tenants" migration
# with this fixed id, and protected from modification through the API.
SYSTEM_TENANT_ID = UUID("cec393c8-9c66-444c-83a7-6f6c941b5153")
