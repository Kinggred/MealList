from datetime import date, datetime, time
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.params import Query
from sqlmodel import Session
from typing_extensions import Annotated

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.meal import meal_crud
from app.crud.meal_dish import meal_dish_crud
from app.crud.shopping_list import shopping_list_crud
from app.models.meal import MealCreateSchema, Meal, MealUpdate, MealView, MealListView
from app.models.meal_dish import MealDishCreateSchema, MealDish, MealDishUpdate
from app.models.schoping_list import ShoppingListView
from app.models.user import User

meal_router = APIRouter()


@meal_router.get("/", response_model=MealListView)
def get_meals(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    date_from: Annotated[date | None, Query()] = date.today(),
    date_to: Annotated[date | None, Query()] = date.today(),
) -> MealListView:
    start_dt = datetime.combine(date_from, time.min)
    end_dt = datetime.combine(date_to, time.max)
    return meal_crud.get_meals_in_range(db, user, start_dt, end_dt)


@meal_router.post("/")
def create_meal(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_to_add: MealCreateSchema,
) -> Meal:
    return meal_crud.create_with_dishes(db, user, meal_to_add)


@meal_router.get(
    "/shopping_list",
    response_model=ShoppingListView,
    responses={
        200: {
            "content": {
                "application/json": {},
                "application/pdf": {},
            },
            "description": "Shopping list as JSON or PDF",
        }
    },
)
def get_shopping_list(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    date_from: Annotated[date | None, Query()] = date.today(),
    date_to: Annotated[date | None, Query()] = date.today(),
    file: bool = False,
):
    if file:
        pdf_bytes = shopping_list_crud.get_file_from_range(db, user, date_from, date_to)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="shopping-list-{date_from}-{date_to}.pdf"'
                )
            },
        )
    return shopping_list_crud.get_list_from_range(db, user, date_from, date_to)


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
    return meal_dish_crud.add_meal_dish(
        db, user=user, meal_id=meal_id, meal_dish=dish_to_add
    )


@meal_router.patch("/{meal_id}/dishes/{connection_id}")
def update_dish(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    connection_id: UUID,
    dish_to_update: MealDishUpdate,
) -> MealDish:
    return meal_dish_crud.safe_update(
        db, user=user, updated_obj_id=connection_id, obj_in=dish_to_update
    )


@meal_router.delete("/{meal_id}/dishes/{connection_id}")
def delete_dish(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    meal_id: UUID,
    connection_id: UUID,
):
    meal_dish_crud.safe_remove(db, user=user, id=connection_id)
