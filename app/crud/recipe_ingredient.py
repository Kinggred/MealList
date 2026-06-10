from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.ingridient import Ingredient
from app.models.recipe_ingredient import (
    RecipeIngredient,
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
)
from app.models.schoping_list import DishesCalculationsView, IngredientsCalculationsView


class CRUDRecipeIngredient(
    CRUDBase[RecipeIngredient, RecipeIngredientCreate, RecipeIngredientUpdate]
):

    def get_ingredient_calculations_from_dishes(
        self,
        db: Session,
        *,
        dishes: list[DishesCalculationsView],
    ) -> list[IngredientsCalculationsView]:
        if not dishes:
            return []

        recipe_ids = [dish.recipe_id for dish in dishes]

        rows = db.exec(
            select(RecipeIngredient, Ingredient)
            .join(
                Ingredient,
                RecipeIngredient.ingredient_id == Ingredient.id,
            )
            .where(
                RecipeIngredient.recipe_id.in_(recipe_ids),
                RecipeIngredient.enabled == True,
                Ingredient.enabled == True,
            )
        ).all()

        return IngredientsCalculationsView.from_recipe_ingredients(
            dishes=dishes,
            rows=rows,
        )


recipe_ingredient_crud = CRUDRecipeIngredient(RecipeIngredient)
