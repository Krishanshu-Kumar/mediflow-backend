from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core import status_codes, messages
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token
from app.crud import auth_users_crud, tenant_crud, role_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=status_codes.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user. Verifies that the tenant and role exist,
    and that the email is unique within the tenant.
    """
    # 1. Verify tenant exists
    tenant = tenant_crud.get_tenant_by_id(db, tenant_id=user_in.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.TENANT_NOT_FOUND,
        )

    # 2. Verify role exists
    role = role_crud.get_role_by_id(db, role_id=user_in.role_id)
    if not role:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.ROLE_NOT_FOUND,
        )

    # 3. Verify email is unique in the tenant
    db_user = auth_users_crud.get_user_by_email_and_tenant(
        db, email=user_in.email, tenant_id=user_in.tenant_id
    )
    if db_user:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.EMAIL_ALREADY_EXISTS,
        )

    return auth_users_crud.create_user(db, user=user_in)


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user via JSON payload and return an access token.
    """
    user = auth_users_crud.authenticate_user(
        db,
        email=login_data.email,
        tenant_id=login_data.tenant_id,
        password=login_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS,
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INACTIVE_USER,
        )

    access_token = create_access_token(subject=UUID(str(user.id)))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-form", response_model=Token)
def login_for_access_token_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible token login (form-data).
    Expects username as 'email' or 'tenant_id|email'.
    If just 'email' is provided, it tries to auto-detect the tenant. If the email
    exists in multiple tenants, it raises an error.
    """
    username = form_data.username
    password = form_data.password

    tenant_id = None
    email = username

    if "|" in username:
        parts = username.split("|", 1)
        try:
            tenant_id = UUID(parts[0])
            email = parts[1]
        except ValueError:
            pass

    if not tenant_id:
        # Resolve tenant_id from email
        users = db.query(AuthUser).filter(AuthUser.email == email).all()
        if not users:
            raise HTTPException(
                status_code=status_codes.HTTP_401_UNAUTHORIZED,
                detail=messages.INVALID_CREDENTIALS,
            )
        if len(users) > 1:
            raise HTTPException(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                detail="Email exists in multiple tenants. Please use format 'tenant_id|email' in username.",
            )
        tenant_id = UUID(str(users[0].tenant_id))

    user = auth_users_crud.authenticate_user(
        db,
        email=email,
        tenant_id=tenant_id,
        password=password,
    )
    if not user:
        raise HTTPException(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_CREDENTIALS,
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INACTIVE_USER,
        )

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
