from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.recipe import recipe_crud
from app.models.recipe import RecipeCreate, Recipe, RecipeCreateView
from app.models.user import User

recipe_router = APIRouter()


@recipe_router.post("/")
def create_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe: RecipeCreateView,
) -> Recipe:
    return recipe_crud.create_with_ingredients(db, user=user, recipe_view=recipe)
