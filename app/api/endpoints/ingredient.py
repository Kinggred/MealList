from typing import List, Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.ingredient import crud_ingredient
from app.crud.ingredient_self_reference import ingredient_self_reference_crud
from app.models.ingredient_self_reference import (
    CreateIngredientTie,
    IngredientSelfReferenceCreate,
)
from app.models.ingridient import (
    Ingredient,
    IngredientResponse,
    IngredientCreate,
    IngredientWithTies,
    IngredientUpdate,
)
from app.models.user import User

ingredient_router = APIRouter()


@ingredient_router.get("/", response_model=Page[IngredientResponse])
def get_ingredients(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
) -> Page[IngredientResponse]:
    return crud_ingredient.paginated_get_all(db)


@ingredient_router.post("/")
def create_ingredient(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    ingredient: IngredientCreate,
):
    return crud_ingredient.create(db=db, user=user, obj_in=ingredient)


@ingredient_router.get("/{ingredient_id}", response_model=IngredientWithTies)
def get_ingredient(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    ingredient_id: str,
):
    return crud_ingredient.get_ingredient_with_ties(db=db, id=ingredient_id)


@ingredient_router.patch("/{ingredient_id}")
def update_ingredient(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    ingredient_id: str,
    ingredient: IngredientUpdate,
) -> IngredientResponse:
    return crud_ingredient.safe_update(
        db=db,
        user=user,
        updated_obj_id=ingredient_id,
        ingredient=ingredient,
    )


@ingredient_router.delete("/{ingredient_id}")
def delete_ingredient(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    ingredient_id: str,
):
    return crud_ingredient.safe_remove(db=db, user=user, id=ingredient_id)


@ingredient_router.post(
    "/ties/{ingredient_id}",
    description="Tie ingredient as an alternative or simply as sub-ingredient",
)
def tie_ingredients(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    create_ingredient_tie: CreateIngredientTie,
    ingredient_id: str,
):
    obj_in = IngredientSelfReferenceCreate(
        **create_ingredient_tie.model_dump(), ingredient_id=ingredient_id
    )
    ingredient_self_reference_crud.create(db=db, user=user, obj_in=obj_in)
