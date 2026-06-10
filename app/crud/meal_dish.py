from typing import List

from sqlmodel import Session, select
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.meal_dish import (
    MealDish,
    MealDishCreate,
    MealDishUpdate,
    MealDishCreateSchema,
)
from app.models.schoping_list import DishesCalculationsView

from app.models.user import User


class CRUDMealDish(CRUDBase[MealDish, MealDishCreate, MealDishUpdate]):
    def add_meal_dish(
        self, db: Session, *, user: User, meal_id: UUID, meal_dish: MealDishCreateSchema
    ) -> MealDish:
        return self.create(
            db=db,
            user=user,
            obj_in=MealDishCreate(**meal_dish.model_dump(), meal_id=meal_id),
        )

    def get_dishes_from_meal_list(
        self,
        db: Session,
        *,
        meal_ids: list[UUID],
    ) -> list[DishesCalculationsView]:
        if not meal_ids:
            return []

        meal_dishes = db.exec(
            select(MealDish).where(
                MealDish.meal_id.in_(meal_ids),
                MealDish.enabled == True,
            )
        ).all()

        return DishesCalculationsView.from_meal_dishes(meal_dishes)


meal_dish_crud = CRUDMealDish(MealDish)
