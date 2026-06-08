from sqlmodel import Session

from app import models
from app.crud.base import CRUDBase
from app.models.user import User, UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_user_by_email(self, db: Session, *, email: str) -> models.User:
        return db.query(models.User).filter(models.User.email == email).first()