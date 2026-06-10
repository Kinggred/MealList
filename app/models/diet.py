from uuid import UUID

from sqlmodel import JSON, Field, Column, SQLModel
from typing import Dict, List
from app.models.base import BaseModel


class Diet(BaseModel, table=True):
    name: str
    content: Dict = Field(default={}, sa_column=Column(JSON))

class DietCreate(SQLModel):
    name: str
    content: Dict = Field(default={}, sa_column=Column(JSON))

class DietUpdate(SQLModel):
    name: str | None
    content: str | None

class DietCreateSchema(SQLModel):
    name: str
    content: str
    ingredients: List[UUID]