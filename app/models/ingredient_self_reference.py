from sqlmodel import Field
from uuid import UUID

from app.models.base import BaseModel


class IngredientSelfReference(BaseModel, table=True):
    __tablename__ = "ingredient_self_reference"
    ingredient_id: UUID = Field(foreign_key="ingredient.id")
    contained_id: UUID = Field(foreign_key="ingredient.id")
