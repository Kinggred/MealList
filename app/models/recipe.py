from sqlmodel import JSON, Field, Column, SQLModel
from typing import Dict, List
from app.models.base import BaseModel
from app.models.recipe_ingredient import RecipeIngredientCreateSchema


class Recipe(BaseModel, table=True):
    name: str
    text: Dict = Field(default={}, sa_column=Column(JSON))
    image: str  # base64


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
