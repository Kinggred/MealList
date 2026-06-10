from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user
from app.api.database import get_session
from app.crud.diet import diet_crud
from app.models.diet import DietCreateSchema, Diet, DietUpdate
from app.models.user import User

diet_router = APIRouter()


@diet_router.get("/")
def get_diets(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_active_user),
) -> Page[Diet]:
    return diet_crud.paginated_get_all(db)


@diet_router.post("/")
def create_diet(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    diet: DietCreateSchema,
) -> Diet:
    return diet_crud.create_with_ingredients(db, user, diet_schema=diet)


@diet_router.get("/{diet_id}")
def get_diet(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    diet_id: UUID,
) -> Diet:
    return diet_crud.safe_get(db, diet_id)


@diet_router.patch("/{diet_id}")
def update_diet(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    diet_id: UUID,
    new_data: DietUpdate,
) -> Diet:
    return diet_crud.safe_update(db, user=user, updated_obj_id=diet_id, obj_in=new_data)


@diet_router.delete("/{diet_id}")
def delete_diet(
    db: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)],
    diet_id: UUID,
):
    diet_crud.safe_remove(db, user, diet_id)
