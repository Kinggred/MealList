from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import BaseModel


class RecipeIngredient(BaseModel, table=True):
    __tablename__ = "recipe_ingredient"
    recipe_id: UUID = Field(foreign_key="recipe.id")
    ingredient_id: UUID = Field(foreign_key="ingredient.id")
    amount: float
    created_by: UUID = Field(default=None, foreign_key="user.id")


class RecipeIngredientCreateSchema(SQLModel):
    ingredient_id: UUID
    amount: float


class RecipeIngredientCreate(RecipeIngredientCreateSchema):
    recipe_id: UUID


class RecipeIngredientUpdate(SQLModel):
    amount: float
