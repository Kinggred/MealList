from sqlmodel import Session, select
from uuid import UUID

from app.crud.base import CRUDBase
from app.crud.recipe_ingredient import recipe_ingredient_crud
from app.models.ingridient import Ingredient
from app.models.recipe import (
    RecipeCreate,
    RecipeUpdate,
    Recipe,
    RecipeCreateSchema,
    RecipeView,
)
from app.models.recipe_ingredient import RecipeIngredientCreate, RecipeIngredient
from app.models.user import User


class CRUDRecipe(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def create_with_ingredients(
        self, db: Session, user: User, recipe_view: RecipeCreateSchema
    ) -> Recipe:
        recipe_create = RecipeCreate(**recipe_view.model_dump())
        recipe = self.create(db, user=user, obj_in=recipe_create)

        for ingredient in recipe_view.ingredients:
            ingredient_to_add = RecipeIngredientCreate(
                **ingredient.model_dump(), recipe_id=recipe.id
            )
            recipe_ingredient_crud.create(db, user=user, obj_in=ingredient_to_add)

        return self.safe_get(db, id=recipe.id)

    def get_recipe_view(
        self, db: Session, user: User, *, recipe_id: UUID
    ) -> RecipeView:
        recipe = self.safe_get(db, user=user, id=recipe_id)
        statement = (
            select(Recipe, RecipeIngredient, Ingredient)
            .join(RecipeIngredient, Recipe.id == RecipeIngredient.recipe_id)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(Recipe.id == recipe_id, Recipe.created_by == user.id)
        )
        recipe_with_dishes = db.exec(statement).all()

        if not recipe_with_dishes:
            return RecipeView(
                id=recipe.id,
                image=recipe.image,
                name=recipe.name,
                text=recipe.text,
                ingredients=[],
            )

        return RecipeView.from_rows(recipe_with_dishes)


recipe_crud = CRUDRecipe(Recipe)
