from sqlmodel import Session
from uuid import UUID

from app.api.exceptions import NotFoundException
from app.crud.base import CRUDBase
from app.models.recipe_ingredient import (
    RecipeIngredient,
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    RecipeIngredientCreateSchema,
)
from app.models.user import User


class CRUDRecipeIngredient(
    CRUDBase[RecipeIngredient, RecipeIngredientCreate, RecipeIngredientUpdate]
):
    pass


recipe_ingredient_crud = CRUDRecipeIngredient(RecipeIngredient)
