import logging
from typing import Any, Dict, Generic, List, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError   # Potential problems ahead - import from sqlmodel
from sqlmodel import Session, SQLModel, select

from app.models.base import BaseModel
from app.api.exceptions import DatabaseException, NotFoundException

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

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

    def get(self, db: Session, id: UUID, *args, **kwargs) -> ModelType | None:
        data = db.exec(select(self.model).where(self.model.id == id)).first()
        if data:
            logger.info(f"Retreived {self.model.__name__}: {id}")
            return data
        raise NotFoundException

    def get_all(
        self,
        db: Session,
        *,
        limit: int,
    ) -> List[ModelType]:
        obj = db.exec(select(self.model).limit(limit)).all()
        logger.info(f"Retreived {len(obj)} {self.model.__name__}s")

        return obj

    def create(self, db: Session, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        obj = self.db_add_operation(db=db, object_to_add=db_obj)
        logger.info(f"Created {self.model.__name__}: {obj.id}")

        return obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]) -> ModelType:
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

    def remove(self, db: Session, *, id: UUID) -> ModelType:
        db_obj = db.exec(select(self.model).where(self.model.id == id)).first()
        if not db_obj:
            raise NotFoundException
        db_obj.enabled = False
        db.commit()
        logger.info(f"Removed {self.model.__name__}: {db_obj.id}")

        return db_obj
