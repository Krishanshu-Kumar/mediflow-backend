from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from jose import JWTError, jwt
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import get_db
from app.core import status_codes, messages
from app.crud import auth_users_crud, role_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import TokenPayload
from typing import cast
from uuid import UUID as UUIDType


# OAuth2 scheme for extracting Bearer token
# reusable_oauth2 = OAuth2PasswordBearer(
#     tokenUrl="/auth/login-form"  # Exposed for Swagger interactive UI login
# )

reusable_oauth2 = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> AuthUser:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if not token_data.sub:
        raise HTTPException(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing subject claim",
        )

    try:
        user_uuid = UUID(token_data.sub)
    except ValueError:
        raise HTTPException(
            status_code=status_codes.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token subject",
        )

    user = auth_users_crud.get_user_by_id(db, user_id=user_uuid)
    if not user:
        raise HTTPException(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    return user

def get_current_active_user(
    current_user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """
    Validate that the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            detail=messages.INACTIVE_USER,
        )
    return current_user


def get_current_super_admin(
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AuthUser:
    """
    Validate that the current active user is a System Super Admin.
    """
    if not current_user.role_id:
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SUPER_ADMIN_REQUIRED,
        )

    role = role_crud.get_role_by_id(db, role_id=cast(UUIDType, current_user.role_id))
    if not role or not bool(role.is_system_role):
        raise HTTPException(
            status_code=status_codes.HTTP_403_FORBIDDEN,
            detail=messages.SUPER_ADMIN_REQUIRED,
        )
    return current_user
