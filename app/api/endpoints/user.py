from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.auth import get_password_hash, get_current_active_user
from app.api.database import get_session
from app.api.exceptions import BadRequestException
from app.crud.user import crud_user
from app.models.user import UserResponse, User, UserCreate, UserCreateSchema

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user(
    db: Annotated[Session, Depends(get_session)], user: UserCreateSchema
) -> UserResponse:
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise BadRequestException

    db_user = crud_user.create_user(
        db, user=user, pwd_hash=get_password_hash(user.password)
    )
    return db_user


@router.get("/me", response_model=UserResponse)
async def get_self(
    user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return user
