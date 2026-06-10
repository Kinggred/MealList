from typing import List

from sqlmodel import Session, select
from uuid import UUID

from app.crud.base import CRUDBase
from app.crud.ingredient import ingredient_crud
from app.models.diet_ingredient import DietIngredient, DietIngredientCreate
from app.models.user import User


class CRUDDietIngredient(
    CRUDBase[DietIngredient, DietIngredientCreate, DietIngredientCreate]
):
    def add_with_derived(
        self, db: Session, user: User, ingredient_ids: List[UUID], diet_id: UUID
    ):
        """
        UNSAFE - precheck if diet exists
        """
        ingredient_ids = ingredient_crud.multi_get_derivative_ids(db, ingredient_ids)
        already_added_ingredients = db.exec(
            select(DietIngredient.id).where(
                DietIngredient.diet_id == diet_id,
                DietIngredient.ingredient_id.in_(ingredient_ids),
            )
        )

        ingredients_to_add = [
            DietIngredientCreate(
                diet_id=diet_id,
                ingredient_id=ingredient_id,
            )
            for ingredient_id in ingredient_ids
            if ingredient_id not in already_added_ingredients
        ]

        self.create_many(db, user=user, objs_in=ingredients_to_add)

    def remove_with_derived(
        self, db: Session, user: User, diet_id: UUID, ingredient_ids: List[UUID]
    ):
        ingredient_ids = ingredient_crud.multi_get_derivative_ids(db, ingredient_ids)

        diet_ingredients_to_remove = db.exec(
            select(DietIngredient.id).where(
                DietIngredient.diet_id == diet_id,
                DietIngredient.ingredient_id.in_(ingredient_ids),
            )
        ).all()
        self.safe_remove_many(db, user=user, ids=diet_ingredients_to_remove, hard=True)


diet_ingredient_crud = CRUDDietIngredient(DietIngredient)
