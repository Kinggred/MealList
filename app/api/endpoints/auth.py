from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.sessions import Session

from app.api.auth import authenticate_user, create_access_token
from app.api.database import get_session
from app.api.exceptions import UnauthorizedException
from app.core.settings import get_settings
from app.models.token import Token

router = APIRouter()
settings = get_settings()

@router.post("/token")
async def login_for_access_token(
    db: Annotated[Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password) # USE EMAIL AS USERNAME
    if not user:
        raise UnauthorizedException
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")