from sqlmodel import Session, select
from uuid import UUID

from app.crud.base import CRUDBase
from app.crud.diet_ingredient import diet_ingredient_crud
from app.models.diet import (
    DietCreate,
    Diet,
    DietUpdate,
    DietCreateSchema,
    DietView,
    UpdateIngredientsInDietSchema,
)
from app.models.diet_ingredient import DietIngredientCreate, DietIngredient
from app.models.ingridient import Ingredient
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

    def get_with_ingredients(self, db: Session, diet_id: UUID) -> DietView:
        statement = (
            select(Diet, Ingredient)
            .join(DietIngredient, Diet.id == DietIngredient.diet_id)
            .join(Ingredient, DietIngredient.ingredient_id == Ingredient.id)
            .where(Diet.id == diet_id)
        )
        rows = db.exec(statement).all()
        return DietView.from_rows(rows)

    def update_ingredients(
        self,
        db: Session,
        user: User,
        diet_id: UUID,
        update_data: UpdateIngredientsInDietSchema,
    ):
        if len(update_data.add) > 0:
            diet_ingredient_crud.add_with_derived(
                db,
                user,
                diet_id,
                update_data.add,
            )
        if len(update_data.remove) > 0:
            diet_ingredient_crud.remove_with_derived(
                db,
                user,
                diet_id,
                update_data.remove,
            )


diet_crud = CRUDDiet(Diet)
