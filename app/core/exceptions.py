from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.core import messages

# Postgres SQLSTATE for a unique/primary key violation
UNIQUE_VIOLATION_SQLSTATE = "23505"

# DB constraint name -> message returned with a 409 when it is violated.
# Add an entry whenever a new unique constraint needs a friendly message.
UNIQUE_CONSTRAINT_MESSAGES = {
    "uq_tb_gl_tenants_slug": messages.TENANT_SLUG_EXISTS,
    "uq_tb_gl_roles_tenant_id_name": messages.ROLE_NAME_EXISTS,
    "uq_tb_auth_users_tenant_id_email": messages.EMAIL_ALREADY_EXISTS,
    "pk_tb_gl_permissions": messages.PERMISSION_CODE_EXISTS,
}


def get_unique_violation_message(exc: IntegrityError) -> Optional[str]:
    """
    Returns the friendly message if `exc` is a unique violation on a registered
    constraint, otherwise None.
    """
    orig = getattr(exc, "orig", None)
    if getattr(orig, "pgcode", None) != UNIQUE_VIOLATION_SQLSTATE:
        return None
    constraint = getattr(getattr(orig, "diag", None), "constraint_name", None)
    if constraint is None:
        return None
    return UNIQUE_CONSTRAINT_MESSAGES.get(constraint)
