from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.diet import diet_crud
from app.models.diet import DietCreateSchema, Diet
from app.models.user import User

diet_router = APIRouter()


@diet_router.post("/")
def create_diet(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    diet: DietCreateSchema,
) -> Diet:
    return diet_crud.create_with_ingredients(db, user, diet_schema=diet)
