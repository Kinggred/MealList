from enum import StrEnum
from typing import List

from sqlmodel import Field, SQLModel
from uuid import UUID
from app.models.base import BaseModel
from app.models.recipe_ingredient import RecipeIngredient


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
class IngredientInRecipeView(SQLModel):
    id: UUID
    name: str
    counted_calories: int
    counted_cost: float
    amount: float
    unit_of_measurement: Units

    @classmethod
    def from_models(
        cls,
        recipe_ingredient: "RecipeIngredient",
        ingredient: Ingredient,
    ) -> IngredientInRecipeView:
        counted_calories = int(
            ingredient.calories
            * recipe_ingredient.amount
            / ingredient.amount_per_cost
        )

        counted_cost = (
            ingredient.cost
            * recipe_ingredient.amount
            / ingredient.amount_per_cost
        )

        return cls(
            id=ingredient.id,
            name=ingredient.name,
            counted_calories=counted_calories,
            counted_cost=round(counted_cost, 2),
            amount=recipe_ingredient.amount,
            unit_of_measurement=ingredient.unit_of_measurement,
        )