from datetime import date
from typing import List
from uuid import UUID

from sqlmodel import Session, select, or_

from app.api.exceptions import NotFoundException
from app.crud.base import CRUDBase, CreateSchemaType, ModelType
from app.crud.ingredient_self_reference import ingredient_self_reference_crud
from app.models.ingredient_self_reference import IngredientSelfReference
from app.models.ingridient import (
    Ingredient,
    IngredientCreate,
    IngredientUpdate,
    IngredientWithTies,
)
from app.models.schoping_list import IngredientsCalculationsView, ShoppingListView
from app.models.user import User


class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    def create(
        self, db: Session, *, user: User | None, obj_in: CreateSchemaType, **kwargs
    ) -> ModelType:
        # VALIDATE and Standardize - units - Done by fastapi parsers already
        return super().create(db, user=user, obj_in=obj_in, **kwargs)

    def get_ingredient_with_ties(self, db: Session, id: UUID) -> IngredientWithTies:
        ingredient = self.safe_get(db, id=id)
        if not ingredient:
            raise NotFoundException
        response = IngredientWithTies(**ingredient.model_dump())

        alternatives_statement = (
            select(self.model)
            .join(
                IngredientSelfReference,
                or_(
                    self.model.id == IngredientSelfReference.ingredient_id,
                    self.model.id == IngredientSelfReference.contained_id,
                ),
            )
            .where(
                self.model.name != ingredient.name,
                IngredientSelfReference.is_alternative == True,
            )
        )
        response.alternatives = db.exec(alternatives_statement).all()
        contained_statement = (
            select(self.model, IngredientSelfReference.include_in_count)
            .join(
                IngredientSelfReference,
                self.model.id == IngredientSelfReference.contained_id,
            )
            .where(
                IngredientSelfReference.ingredient_id == ingredient.id,
                IngredientSelfReference.is_alternative == False,
            )
        )

        # TODO: Move into validator
        for ingredient, include_in_count in db.exec(contained_statement).all():
            if include_in_count:
                response.contains.counted.append(ingredient)
            else:
                response.contains.uncounted.append(ingredient)

        return response

    def get_derivatives(
        self, db: Session, *, ingredient_id: UUID
    ) -> IngredientSelfReference:
        return ingredient_self_reference_crud.get_ids_of_derivatives(db, ingredient_id)

    def multi_get_derivative_ids(
        self,
        db: Session,
        *,
        ingredients_ids: list[UUID],
    ) -> list[UUID]:
        return ingredient_self_reference_crud.multi_get_ids_of_derivatives(
            db,
            ids=ingredients_ids,
        )

    def build_shopping_list(
        self,
        db: Session,
        *,
        date_from: date,
        date_to: date,
        calculations: list[IngredientsCalculationsView],
    ) -> ShoppingListView:
        ingredient_ids = [calculation.ingredient_id for calculation in calculations]

        ingredients = db.exec(
            select(Ingredient).where(
                Ingredient.id.in_(ingredient_ids),
                Ingredient.enabled == True,
            )
        ).all()

        return ShoppingListView.from_calculations(
            date_from=date_from,
            date_to=date_to,
            calculations=calculations,
            ingredients=ingredients,
        )


ingredient_crud = CRUDIngredient(Ingredient)
