from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import get_db
from app.core import status_codes, messages
from app.crud import auth_users_crud
from app.models.Users.auth_users_model import AuthUser
from app.schemas.Users.auth_users_schema import TokenPayload

# OAuth2 scheme for extracting Bearer token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/login-form"  # Exposed for Swagger interactive UI login
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> AuthUser:
    """
    Validate credentials from the JWT token and return the authenticated user.
    """
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
