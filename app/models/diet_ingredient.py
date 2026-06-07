from sqlmodel import Field
from uuid import UUID

from app.models.base import BaseModel


class DietIngredient(BaseModel, table=True):
    __tablename__ = 'diet_ingredient'
    ingredient_id: UUID = Field(foreign_key="ingredient.id")
    diet_id: UUID = Field(foreign_key="diet.id")
