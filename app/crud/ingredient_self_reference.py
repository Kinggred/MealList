from typing import List
from uuid import UUID

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.ingredient_self_reference import (
    IngredientSelfReference,
    IngredientSelfReferenceCreate,
    IngredientSelfReferenceUpdate,
)


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

    def multi_get_ids_of_derivatives(
        self,
        db: Session,
        ids: list[UUID],
    ) -> list[UUID]:
        if not ids:
            return []

        statement = select(IngredientSelfReference.contained_id).where(
            IngredientSelfReference.ingredient_id.in_(ids),
            IngredientSelfReference.is_alternative == False,
            IngredientSelfReference.enabled == True,
        )

        derived_ids = db.exec(statement).all()

        return list(set(ids + derived_ids))


ingredient_self_reference_crud = CRUDIngredientSelfReference(IngredientSelfReference)
