from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import BaseModel
from app.models.recipe import RecipeInDishView


class MealDish(BaseModel, table=True):
    __tablename__ = "meal_dish"
    meal_id: UUID = Field(foreign_key="meal.id")
    recipe_id: UUID = Field(foreign_key="recipe.id")
    full_portions: int
    half_portions: int
    created_by: UUID = Field(default=None, foreign_key="user.id")


class MealDishCreate(SQLModel):
    meal_id: UUID
    recipe_id: UUID
    full_portions: int
    half_portions: int


class MealDishUpdate(SQLModel):
    full_portions: int | None
    half_portions: int | None


class MealDishCreateSchema(SQLModel):
    recipe_id: UUID
    full_portions: int
    half_portions: int


class MealDishView(SQLModel):
    connection_id: UUID
    recipe: RecipeInDishView
    full_portions: int
    half_portions: int
