from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class RecipeIngredient(BaseModel, table=True):
    __tablename__ = 'recipe_ingredient'
    recipe_id: UUID = Field(foreign_key="recipe.id")
    ingredient_id: UUID = Field(foreign_key="ingredient.id")
    amount: float
