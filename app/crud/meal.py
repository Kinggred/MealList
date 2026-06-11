from datetime import datetime
from typing import List

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.crud.meal_dish import meal_dish_crud
from app.models.meal import (
    Meal,
    MealCreate,
    MealUpdate,
    MealCreateSchema,
    MealView,
    MealListView,
)
from app.models.meal_dish import MealDishCreate, MealDish
from app.models.recipe import Recipe
from app.models.user import User


class CRUDMeal(CRUDBase[Meal, MealCreate, MealUpdate]):
    def get_meals_in_range(
        self,
        db: Session,
        user: User,
        start_date: datetime,
        end_date: datetime,
    ) -> MealListView:
        statement = (
            select(self.model)
            .where(
                self.model.enabled == True,
                self.model.created_by == user.id,
                self.model.date >= start_date,
                self.model.date <= end_date,
            )
            .order_by(self.model.date)
        )

        results = db.exec(statement).all()

        return MealListView(results=results)

    def create_with_dishes(
        self, db: Session, user: User, meal_schema: MealCreateSchema
    ) -> Meal:
        meal_create = MealCreate(**meal_schema.model_dump())
        meal_in_db = self.create(db=db, user=user, obj_in=meal_create)

        for dish in meal_schema.dishes:
            # TODO: Push many at once to db, will do for POC
            dish_schema = MealDishCreate(**dish.model_dump(), meal_id=meal_in_db.id)
            meal_dish_crud.create(db=db, user=user, obj_in=dish_schema)
        return self.safe_get(db, id=meal_in_db.id)

    def get_with_dishes(self, db: Session, user: User, meal_id: int) -> MealView:
        self.safe_get(db, id=meal_id)
        statement = (
            select(Meal, MealDish, Recipe)
            .outerjoin(
                MealDish,
                (MealDish.meal_id == Meal.id) & (MealDish.enabled == True),
            )
            .outerjoin(
                Recipe,
                (Recipe.id == MealDish.recipe_id) & (Recipe.enabled == True),
            )
            .where(
                Meal.id == meal_id,
                Meal.enabled == True,
            )
        )
        meal_with_dishes = db.exec(statement).all()
        return MealView.from_rows(meal_with_dishes)


meal_crud = CRUDMeal(Meal)
