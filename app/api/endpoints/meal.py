from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing_extensions import Annotated

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.meal import meal_crud
from app.models.meal import MealCreateSchema, Meal
from app.models.user import User

meal_router = APIRouter()


@meal_router.post("/")
def create_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_to_add: MealCreateSchema,
) -> Meal:
    return meal_crud.create_with_dishes(db, user, meal_to_add)
