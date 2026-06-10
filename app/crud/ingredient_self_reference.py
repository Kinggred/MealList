from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase, CreateSchemaType, ModelType
from app.models.ingredient_self_reference import (
    IngredientSelfReference,
    IngredientSelfReferenceCreate,
    IngredientSelfReferenceUpdate,
)
from app.models.user import User


class CRUDIngredientSelfReference(
    CRUDBase[
        IngredientSelfReference,
        IngredientSelfReferenceCreate,
        IngredientSelfReferenceUpdate,
    ]
):
    def get_ids_of_alternatives(
        self, db: Session, id: UUID
    ) -> list[IngredientSelfReference]:
        alternatives = db.exec(
            select(self.model.id).where(self.model.ingredient_id == id)
        ).all()
        return alternatives


ingredient_self_reference_crud = CRUDIngredientSelfReference(IngredientSelfReference)
