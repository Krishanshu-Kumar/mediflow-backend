"""
Create a platform Super Admin (a user in the MediFlow tenant with the Super Admin role).

Every API that creates users needs a logged-in Super Admin, so the first one
has to be made from the command line:

    python -m app.scripts.create_super_admin
"""
from getpass import getpass

from pydantic import ValidationError

from app.core.constants import SUPER_ADMIN_ROLE_ID, SYSTEM_TENANT_ID
from app.core.database import SessionLocal
from app.crud import auth_users_crud
from app.schemas.Users.auth_users_schema import UserCreate


def main() -> None:
    email = input("Email: ")
    full_name = input("Full name: ")
    password = getpass("Password (min 8 chars): ")
    if getpass("Repeat password: ") != password:
        raise SystemExit("Passwords do not match")

    try:
        user_in = UserCreate(
            tenant_id=SYSTEM_TENANT_ID,
            role_id=SUPER_ADMIN_ROLE_ID,
            email=email,
            full_name=full_name,
            password=password,
        )
    except ValidationError as e:
        raise SystemExit(str(e))

    with SessionLocal() as db:
        if auth_users_crud.get_user_by_email_and_tenant(db, user_in.email, SYSTEM_TENANT_ID):
            raise SystemExit(f"{user_in.email} already exists in the MediFlow tenant")
        user = auth_users_crud.create_user(db, user_in)
        print(f"Created Super Admin {user.email} (id {user.id})")


if __name__ == "__main__":
    main()
