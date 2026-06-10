from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.recipe import recipe_crud
from app.crud.recipe_ingredient import recipe_ingredient_crud
from app.models.recipe import (
    RecipeCreate,
    Recipe,
    RecipeCreateSchema,
    RecipeUpdate,
    RecipeView,
)
from app.models.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientCreateSchema,
)
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
) -> RecipeView:
    return recipe_crud.get_recipe_view(db, user=user, recipe_id=recipe_id)


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


@recipe_router.post("/{recipe_id}/ingredients")
def add_ingredient_to_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
    recipe_ingredient: RecipeIngredientCreateSchema,
):
    recipe_ingredient_crud.create(
        db,
        user=user,
        obj_in=RecipeIngredientCreate(
            **recipe_ingredient.model_dump(), recipe_id=recipe_id
        ),
    )


@recipe_router.patch("/{recipe_id}/ingredients/{connection_id}")
def update_ingredient_to_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
    connection_id: UUID,
    update_data: RecipeUpdate,
):
    recipe_ingredient_crud.safe_update(
        db, user=user, updated_obj_id=connection_id, obj_in=update_data
    )


@recipe_router.delete("/{recipe_id}/ingredients/{connection_id}")
def delete_ingredient_from_recipe(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    recipe_id: UUID,
    connection_id: UUID,
):
    recipe_ingredient_crud.safe_remove(db, user=user, id=connection_id, hard=True)
