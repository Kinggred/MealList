from sqlmodel import Session
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.meal_dish import (
    MealDish,
    MealDishCreate,
    MealDishUpdate,
    MealDishCreateSchema,
)
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


meal_dish_crud = CRUDMealDish(MealDish)
