from sqlmodel import Session

from app.crud.base import CRUDBase, CreateSchemaType, ModelType
from app.crud.recipe_ingredient import recipe_ingredient_crud
from app.models.recipe import RecipeCreate, RecipeUpdate, Recipe, RecipeCreateView
from app.models.recipe_ingredient import RecipeIngredientCreate
from app.models.user import User


class CRUDRecipe(CRUDBase[Recipe, RecipeCreate, RecipeUpdate]):
    def create_with_ingredients(
        self, db: Session, user: User, recipe_view: RecipeCreateView
    ) -> Recipe:
        recipe_create = RecipeCreate(**recipe_view.model_dump())
        recipe = self.create(db, user=user, obj_in=recipe_create)

        for ingredient in recipe_view.ingredients:
            ingredient_to_add = RecipeIngredientCreate(
                **ingredient.model_dump(), recipe_id=recipe.id
            )
            recipe_ingredient_crud.create(db, user=user, obj_in=ingredient_to_add)

        return recipe


recipe_crud = CRUDRecipe(Recipe)
