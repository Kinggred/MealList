from app.crud.base import CRUDBase
from app.models.recipe_ingredient import (
    RecipeIngredient,
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
)


class CRUDRecipeIngredient(
    CRUDBase[RecipeIngredient, RecipeIngredientCreate, RecipeIngredientUpdate]
):
    # TODO: Validation - does ingredient exist? etc
    pass


recipe_ingredient_crud = CRUDRecipeIngredient(RecipeIngredient)
