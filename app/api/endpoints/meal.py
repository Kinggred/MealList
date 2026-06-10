from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlmodel import Session
from typing_extensions import Annotated

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.meal import meal_crud
from app.models.meal import MealCreateSchema, Meal, MealUpdate
from app.models.user import User

meal_router = APIRouter()


@meal_router.get("/", response_model=Page[Meal])
def get_meals(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
) -> Page[Meal]:
    return meal_crud.paginated_get_all(db)


@meal_router.post("/")
def create_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_to_add: MealCreateSchema,
) -> Meal:
    return meal_crud.create_with_dishes(db, user, meal_to_add)


@meal_router.get("/{meal_id}")
def get_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
) -> Meal:
    return meal_crud.get(db, meal_id)


@meal_router.patch("/{meal_id}")
def update_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    update_data: MealUpdate,
) -> Meal:
    return meal_crud.safe_update(
        db, user=user, updated_obj_id=meal_id, obj_in=update_data
    )


@meal_router.delete("/{meal_id}")
def delete_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
):
    return meal_crud.safe_remove(db, user=user, id=meal_id)
