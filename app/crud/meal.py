from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.crud.meal_dish import meal_dish_crud
from app.models.meal import Meal, MealCreate, MealUpdate, MealCreateSchema, MealView
from app.models.meal_dish import MealDishCreate, MealDish
from app.models.recipe import Recipe
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

    def get_with_dishes(self, db: Session, user: User, meal_id: int) -> MealView:
        statement = (
            select(self.model, MealDish, Recipe)
            .join(MealDish, MealDish.meal_id == self.model.id)
            .join(Recipe, Recipe.id == MealDish.recipe_id)
            .where(self.model.id == meal_id, self.model.created_by == user.id)
        )
        meal_with_dishes = db.exec(statement).all()
        return MealView.from_rows(meal_with_dishes)


meal_crud = CRUDMeal(Meal)
