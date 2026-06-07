
from sqlmodel import Field
from uuid import UUID
from app.models.base import BaseModel


class Ingredient(BaseModel, table=True):
    name: str
    calories: int
    cost : float
    amount_per_cost: float
    unit_of_measurement: str # No storing enums in DB as it is a pain
    animal_produced: bool
    animal_derived: bool

    created_by: UUID = Field(default=None, foreign_key="user.id")



