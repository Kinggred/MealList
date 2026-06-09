from sqlmodel import Field, SQLModel
from uuid import UUID

from app.models.base import BaseModel


class IngredientSelfReference(BaseModel, table=True):
    __tablename__ = "ingredient_self_reference"
    ingredient_id: UUID = Field(foreign_key="ingredient.id")
    contained_id: UUID = Field(foreign_key="ingredient.id")  # RENAME TO BASE INGREDIENT
    is_alternative: bool = Field(default=False)
    include_in_count: bool = Field(default=False)


class IngredientSelfReferenceCreate(SQLModel):
    ingredient_id: UUID
    contained_id: UUID
    is_alternative: bool
    include_in_count: bool


class IngredientSelfReferenceUpdate(SQLModel):
    ingredient_id: UUID | None
    contained_id: UUID | None
    is_alternative: bool | None
    include_in_count: bool | None


class CreateIngredientTie(SQLModel):
    contained_id: UUID
    is_alternative: bool = False
    include_in_count: bool = False
