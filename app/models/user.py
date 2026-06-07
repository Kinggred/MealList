from app.models.base import BaseModel
from sqlmodel import SQLModel

class User(BaseModel, table=True):
    username: str | None
    email: str
    password_hash: str

class UserRegistration(SQLModel):
    username: str | None = ""
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserResponse(SQLModel):
    username: str
    email: str
    #  # of recipes or other stuff
