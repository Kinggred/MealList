from sqlmodel import Session

from app import models
from app.crud.base import CRUDBase
from app.models.user import User, UserCreate, UserUpdate, UserCreateSchema


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_user_by_email(self, db: Session, *, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, *, user: UserCreateSchema, pwd_hash) -> User:
        db_user = UserCreate(**user.model_dump(exclude={"password"}),password_hash = pwd_hash,)
        return self.create(db, obj_in=db_user)

crud_user = CRUDUser(User)