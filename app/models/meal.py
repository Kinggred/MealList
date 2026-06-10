from datetime import datetime
from typing import List

from sqlmodel import SQLModel

from app.models.base import BaseModel
from app.models.meal_dish import MealDishCreateSchema


class MealCreate(SQLModel):
    name: str
    date: datetime


class Meal(BaseModel, MealCreate, table=True):
    pass


class MealUpdate(SQLModel):
    name: str | None
    date: datetime | None


class MealCreateSchema(SQLModel):
    name: str
    date: datetime
    dishes: List[MealDishCreateSchema]
