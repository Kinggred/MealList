from sqlmodel import Field, SQLModel
from uuid import UUID
from app.models.base import BaseModel


class IngredientCreate(SQLModel):
    name: str
    calories: int
    cost: float
    amount_per_cost: float
    unit_of_measurement: str
    animal_produced: bool
    animal_derived: bool


class Ingredient(BaseModel, IngredientCreate, table=True):
    created_by: UUID = Field(default=None, foreign_key="user.id")


class IngredientUpdate(SQLModel):
    name: str | None
    calories: int | None
    cost: float | None
    amount_per_cost: float | None
    unit_of_measurement: str | None
    animal_produced: bool | None
    animal_derived: bool | None


class IngredientResponse(IngredientCreate):
    id: UUID
