from datetime import datetime
from pprint import pprint
from typing import List

from sqlmodel import SQLModel, Field
from uuid import UUID

from app.api.exceptions import InternalServerException
from app.models.base import BaseModel
from app.models.meal_dish import MealDishCreateSchema, MealDishView


class MealCreate(SQLModel):
    name: str
    date: datetime


class Meal(BaseModel, MealCreate, table=True):
    created_by: UUID = Field(default=None, foreign_key="user.id")


class MealUpdate(SQLModel):
    name: str | None
    date: datetime | None


class MealCreateSchema(SQLModel):
    name: str
    date: datetime
    dishes: List[MealDishCreateSchema]

class MealView(SQLModel):
    name: str
    date: datetime
    dishes: List[MealDishView]

    @classmethod
    def from_rows(cls, rows) -> MealView:
        """
        :param rows: (Meal, MealDish, Recipe)
        :return: MealView
        """
        try:
            meal = rows[0][0]
        except IndexError:
            raise InternalServerException(code=1)

        return cls(
            name=meal.name,
            date=meal.date,
            dishes=[
                MealDishView(
                    recipe=recipe,
                    full_portions=meal_dish.full_portions,
                    half_portions=meal_dish.half_portions,
                )
                for _, meal_dish, recipe in rows
            ],
        )