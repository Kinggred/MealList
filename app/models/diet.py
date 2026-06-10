from uuid import UUID

from sqlmodel import JSON, Field, Column, SQLModel
from typing import Dict, List
from app.models.base import BaseModel
from app.models.ingridient import IngredientInDietView


class Diet(BaseModel, table=True):
    name: str
    content: Dict = Field(default={}, sa_column=Column(JSON))
    created_by: UUID = Field(default=None, foreign_key="user.id")


class DietCreate(SQLModel):
    name: str
    content: Dict = Field(default={}, sa_column=Column(JSON))


class DietUpdate(SQLModel):
    name: str | None
    content: str | None


class DietCreateSchema(SQLModel):
    name: str
    content: dict[str, str] = {}
    ingredients: List[UUID]

class DietView(SQLModel):
    id: int
    name: str
    content: dict[str, str]
    ingredients: List[IngredientInDietView]