import logging
from typing import Any, Dict, Generic, List, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import (
    IntegrityError,
)  # Potential problems ahead - import from sqlmodel
from sqlmodel import Session, SQLModel, select

from app.models.base import BaseModel
from app.api.exceptions import DatabaseException, NotFoundException, ForbiddenException
from app.models.user import User

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.assigned = True if "created_by" in self.model.model_fields else False
        self.delete_softly = True if "enabled" in self.model.model_fields else False

    # TODO: Consider adding some kind of rollback on error.
    def db_add_operation(self, db: Session, object_to_add: ModelType) -> ModelType:
        try:
            db.add(object_to_add)
            db.commit()
            db.refresh(object_to_add)
        except IntegrityError as error:
            logger.error(f"Database error: {error.orig}")
            raise DatabaseException()
        logger.info(f"Added {self.model.__name__}: {object_to_add.id}")

        return object_to_add

    def safe_get(self, db: Session, id: UUID, *args, **kwargs) -> ModelType:
        data = self.get(db, id)
        if data:
            logger.info(f"Retreived {self.model.__name__}: {id}")
            return data
        raise NotFoundException

    def get(self, db: Session, id: UUID, *args, **kwargs) -> ModelType | None:
        statement = select(self.model).where(
            self.model.id == id, self.model.enabled == True
        )
        data = db.exec(statement).first()

    def get_all(
        self,
        db: Session,
        *,
        limit: int,
    ) -> List[ModelType]:
        obj = db.exec(
            select(self.model).where(self.model.enabled == True).limit(limit)
        ).all()
        logger.info(f"Retreived {len(obj)} {self.model.__name__}s")

        return obj

    def paginated_get_all(self, db: Session) -> Page[ModelType]:
        statement = (
            select(self.model)
            .where(self.model.enabled == True)
            .order_by(self.model.created_at)
        )

        return paginate(db, statement)

    def create(
        self, db: Session, *, user: User | None, obj_in: CreateSchemaType, **kwargs
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        if self.assigned:
            if user is None:
                raise DatabaseException
            db_obj.created_by = user.id
        obj = self.db_add_operation(db=db, object_to_add=db_obj)
        logger.info(f"Created {self.model.__name__}: {obj.id}")

        return obj

    def safe_update(
        self,
        db: Session,
        *,
        user: User,
        updated_obj_id: UUID,
        obj_in: UpdateSchemaType,
        **kwargs,
    ) -> ModelType:
        current_obj = self.safe_get(db, updated_obj_id)
        if user.id != current_obj.created_by:
            raise ForbiddenException
        return self.update(db, db_obj=current_obj, obj_in=obj_in)

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        obj = self.db_add_operation(db=db, object_to_add=db_obj)
        logger.info(f"Updated {self.model.__name__}: {obj.id}")

        return obj

    def safe_remove(self, db: Session, user: User, *, id: UUID) -> ModelType:
        # TODO: Add checks for resources using the one removed
        db_obj = self.safe_get(db, id)
        if user.id != db_obj.created_by:
            raise ForbiddenException
        return self.remove(db, db_obj=db_obj)

    def remove(self, db: Session, *, db_obj: ModelType) -> ModelType:
        db_obj.enabled = False
        db.commit()
        logger.info(f"Removed {self.model.__name__}: {db_obj.id}")

        return db_obj
