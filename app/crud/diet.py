from typing import List
from uuid import UUID

from sqlmodel import Session

from app.crud.base import CRUDBase
from app.crud.diet_ingredient import diet_ingredient_crud
from app.models.diet import DietCreate, Diet, DietUpdate, DietCreateSchema
from app.models.diet_ingredient import DietIngredientCreate, DietIngredient
from app.models.user import User


class CRUDDiet(CRUDBase[Diet, DietCreate, DietUpdate]):
    def create_with_ingredients(
        self, db: Session, user: User, diet_schema: DietCreateSchema
    ) -> Diet:
        diet = self.create(db, user=user, obj_in=DietCreate(**diet_schema.model_dump()))
        for ingredient_id in diet_schema.ingredients:
            diet_ingredient_create = DietIngredientCreate(
                ingredient_id=ingredient_id, diet_id=diet.id
            )
            diet_ingredient_crud.create(db, user=user, obj_in=diet_ingredient_create)
        return diet


diet_crud = CRUDDiet(DietIngredient)
