from sqlmodel import JSON, Field, Column, SQLModel
from typing import Dict, List

from uuid import UUID

from app.models.base import BaseModel
from app.models.recipe_ingredient import RecipeIngredientCreateSchema


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
    name: str | None
    text: dict[str, str] | None
    image: str | None

class RecipeInDishView(SQLModel):
    id: UUID
    name: str