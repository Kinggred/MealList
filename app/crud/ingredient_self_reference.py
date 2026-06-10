from typing import List
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

    def get_ids_of_derivatives(self, db: Session, id: UUID) -> List[UUID]:
        derivatives = db.exec(
            select(IngredientSelfReference.id).where(
                IngredientSelfReference.contained_id == id,
                IngredientSelfReference.is_alternative == False,
            )
        ).all()
        return derivatives

    def multi_get_ids_of_derivatives(self, db: Session, ids: list[UUID]) -> list[UUID]:
        statement = select(IngredientSelfReference).where(
            IngredientSelfReference.contained_id.in_(ids),
            IngredientSelfReference.is_alternative == False,
        )
        return db.exec(statement).all()


ingredient_self_reference_crud = CRUDIngredientSelfReference(IngredientSelfReference)
