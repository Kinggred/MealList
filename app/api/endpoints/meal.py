from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlmodel import Session
from typing_extensions import Annotated

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.meal import meal_crud
from app.crud.meal_dish import meal_dish_crud
from app.models.meal import MealCreateSchema, Meal, MealUpdate, MealView
from app.models.meal_dish import MealDishCreateSchema, MealDish, MealDishUpdate
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
) -> MealView:
    return meal_crud.get_with_dishes(db, user, meal_id)


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


@meal_router.post("/{meal_id}/dishes")
def add_dish(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    dish_to_add: MealDishCreateSchema,
) -> MealDish:
    return meal_dish_crud.add_meal_dish(db, user, meal_id, dish_to_add)


@meal_router.patch("/{meal_id}/dishes/{meal_dish_id}")
def update_dish(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    meal_dish_id: UUID,
    dish_to_update: MealDishUpdate,
) -> MealDish:
    return meal_dish_crud.safe_update(
        db, user=user, id=meal_dish_id, obj_in=dish_to_update
    )


@meal_router.delete("/{meal_id}/dishes/{meal_dish_id}")
def delete_dish(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    meal_dish_id: UUID,
):
    meal_dish_crud.safe_remove(db, user=user, id=meal_dish_id)
