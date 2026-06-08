from uuid import UUID

from app.models.base import BaseModel
from sqlmodel import SQLModel

class User(BaseModel, table=True):
    username: str | None
    email: str
    password_hash: str

class UserCreateSchema(SQLModel):
    username: str | None = ""
    email: str
    password: str

class UserCreate(SQLModel):
    username: str | None = ""
    email: str
    password_hash: str

class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


class UserLogin(SQLModel):
    email: str
    password: str

class UserResponse(SQLModel):
    id: UUID
    username: str
    email: str
    #  # of recipes or other stuff
