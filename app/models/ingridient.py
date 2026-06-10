from enum import StrEnum
from typing import List

from sqlmodel import Field, SQLModel
from uuid import UUID
from app.models.base import BaseModel


class Units(StrEnum):
    milliliter = "ml"
    gram = "g"
    piece = "p"


class Ingredient(BaseModel, table=True):
    name: str
    calories: int
    cost: float
    amount_per_cost: float
    unit_of_measurement: str
    animal_produced: bool
    animal_derived: bool

    created_by: UUID = Field(default=None, foreign_key="user.id")


class IngredientCreate(SQLModel):
    name: str
    calories: int
    cost: float
    amount_per_cost: float
    unit_of_measurement: Units
    animal_produced: bool
    animal_derived: bool


class IngredientUpdate(SQLModel):
    name: str | None
    calories: int | None
    cost: float | None
    amount_per_cost: float | None
    unit_of_measurement: Units | None
    animal_produced: bool | None
    animal_derived: bool | None


class IngredientResponse(IngredientCreate):
    id: UUID


class ContainedIngredients(SQLModel):
    counted: List[Ingredient] = []
    uncounted: List[Ingredient] = []


class IngredientWithTies(IngredientCreate):
    id: UUID
    alternatives: List[Ingredient] = []
    contains: ContainedIngredients = ContainedIngredients()

class IngredientInDietView(SQLModel):
    id: UUID
    name: str
    animal_produced: bool
    animal_derived: bool

    @classmethod
    def from_model(cls, ingredient: Ingredient) -> IngredientInDietView:
        return cls(
            id=ingredient.id,
            name=ingredient.name,
            animal_produced=ingredient.animal_produced,
            animal_derived=ingredient.animal_derived,
        )