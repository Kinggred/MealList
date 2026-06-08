from typing import List, Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlmodel import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.ingredient import crud_ingredient
from app.models.ingridient import Ingredient, IngredientResponse
from app.models.user import User

ingredient_router = APIRouter()


@ingredient_router.get("/")
def get_ingredients(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
) -> Page[IngredientResponse]:
    ingredients = crud_ingredient.paginated_get_all(db)
    return ingredients
