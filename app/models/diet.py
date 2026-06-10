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
    id: UUID
    name: str
    content: dict[str, str]
    ingredients: List[IngredientInDietView]

    @classmethod
    def from_rows(cls, rows) -> DietView:
        """
        :param rows: (Diet Ingredients)
        :return: DietView
        """
        diet = rows[0][0]

        return cls(
            id=diet.id,
            name=diet.name,
            content=diet.content,
            ingredients=[
                IngredientInDietView.from_model(ingredient, connection_id)
                for _, connection_id, ingredient in rows
            ],
        )


class UpdateIngredientsInDietSchema(SQLModel):
    add: List[UUID]
    remove: List[UUID]
