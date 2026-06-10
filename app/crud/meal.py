from sqlmodel import Session

from app.crud.base import CRUDBase
from app.crud.meal_dish import meal_dish_crud
from app.models.meal import Meal, MealCreate, MealUpdate, MealCreateSchema
from app.models.meal_dish import MealDishCreate
from app.models.user import User


class CRUDMeal(CRUDBase[Meal, MealCreate, MealUpdate]):
    def create_with_dishes(
        self, db: Session, user: User, meal_schema: MealCreateSchema
    ) -> Meal:
        meal_create = MealCreate(**meal_schema.model_dump())
        meal_in_db = self.create(db=db, user=user, obj_in=meal_create)

        for dish in meal_schema.dishes:
            # TODO: Push many at once to db, will do for POC
            dish_schema = MealDishCreate(**dish.model_dump(), meal_id=meal_in_db.id)
            meal_dish_crud.create(db=db, user=user, obj_in=dish_schema)
        return meal_in_db


meal_crud = CRUDMeal(Meal)
