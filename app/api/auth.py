from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session

from app.api.database import get_session
from app.api.exceptions import UnauthorizedException
from app.core.settings import get_settings
from app.models.token import TokenData
from app.models.user import User
from app.crud.user import crud_user

pwd_hash = PasswordHash.recommended()
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_hash.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = crud_user.get_user_by_email(db, email=email)
    if user and not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    db: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.safe_get("sub")
        if email is None:
            raise UnauthorizedException
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise UnauthorizedException
    user = crud_user.get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise UnauthorizedException
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.enabled:
        raise UnauthorizedException
    return current_user
