from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.recipe import recipe_crud
from app.models.recipe import RecipeCreate, Recipe, RecipeCreateSchema, RecipeUpdate
from app.models.user import User

recipe_router = APIRouter()


@recipe_router.get("/")
def get_recipes(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
) -> Page[Recipe]:
    return recipe_crud.paginated_get_all(db)


@recipe_router.post("/")
def create_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe: RecipeCreateSchema,
) -> Recipe:
    return recipe_crud.create_with_ingredients(db, user=user, recipe_view=recipe)


@recipe_router.get("/{recipe_id}")
def get_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
) -> Recipe:
    return recipe_crud.safe_get(db, id=recipe_id)


@recipe_router.patch("/{recipe_id}")
def update_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
    update_data: RecipeUpdate,
) -> Recipe:
    return recipe_crud.safe_update(
        db, user=user, updated_obj_id=recipe_id, obj_in=update_data
    )


@recipe_router.delete("/{recipe_id}")
def delete_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
):
    return recipe_crud.safe_delete(db, id=recipe_id)
