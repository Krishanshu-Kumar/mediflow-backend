from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.core import status_codes, messages
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token, verify_password
from app.crud.base import commit_refresh
from app.crud import auth_users_crud, tenant_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import (
    UserResponse,
    UserLogin,
    Token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Log in with hospital slug + email + password and return an access token.
    A wrong slug, email or password all give the same error, so nobody can
    use this endpoint to find out which hospitals or emails exist.
    """
    invalid_credentials = HTTPException(
        status_code=status_codes.HTTP_401_UNAUTHORIZED,
        detail=messages.INVALID_CREDENTIALS,
    )

    tenant = tenant_crud.get_tenant_by_slug(db, slug=login_data.tenant_slug.strip().lower())
    if not tenant:
        raise invalid_credentials

    user = auth_users_crud.get_user_by_email_and_tenant(
        db, email=login_data.email, tenant_id=UUID(str(tenant.id))
    )
    if not user or not verify_password(login_data.password, str(user.hashed_password)):
        raise invalid_credentials

    # Only tell the caller about inactive accounts after the password was right
    if not tenant.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.INACTIVE_TENANT,
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INACTIVE_USER,
        )

    user.last_login_at = datetime.now(timezone.utc)
    commit_refresh(db, user)

    access_token = create_access_token(subject=UUID(str(user.id)))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: AuthUser = Depends(get_current_active_user),
):
    """
    Get details of the currently authenticated active user.
    """
    return current_user
