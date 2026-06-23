from sqlmodel import JSON, Field, Column, SQLModel
from typing import Dict, List

from uuid import UUID

from app.models.base import BaseModel
from app.models.ingridient import IngredientInRecipeView, Ingredient
from app.models.recipe_ingredient import RecipeIngredientCreateSchema, RecipeIngredient


class Recipe(BaseModel, table=True):
    name: str
    text: Dict = Field(default={}, sa_column=Column(JSON))
    image: str  # base64
    created_by: UUID = Field(default=None, foreign_key="user.id")


class RecipeCreate(SQLModel):
    name: str
    text: dict[str, str] = {}
    image: str


class RecipeCreateSchema(RecipeCreate):
    ingredients: List[RecipeIngredientCreateSchema]


class RecipeUpdate(SQLModel):
    name: str | None = None
    text: dict[str, str] | None = None
    image: str | None = None


class RecipeInDishView(SQLModel):
    id: UUID
    name: str


class RecipeView(SQLModel):
    id: UUID
    name: str
    text: dict[str, str] | None
    image: str | None
    ingredients: list[IngredientInRecipeView] | None = []
    total_cost: float | None = 0
    total_calories: float | None = 0

    @classmethod
    def from_rows(
        cls,
        rows: list[tuple[Recipe, RecipeIngredient, Ingredient]],
    ) -> "RecipeView":
        recipe = rows[0][0]

        ingredients = [
            IngredientInRecipeView.from_models(
                recipe_ingredient=recipe_ingredient,
                ingredient=ingredient,
            )
            for _, recipe_ingredient, ingredient in rows
        ]

        return cls(
            id=recipe.id,
            name=recipe.name,
            text=recipe.text,
            image=recipe.image,
            ingredients=ingredients,
            total_cost=round(
                sum(ingredient.counted_cost for ingredient in ingredients),
                2,
            ),
            total_calories=sum(
                ingredient.counted_calories for ingredient in ingredients
            ),
        )
