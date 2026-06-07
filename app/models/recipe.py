from sqlmodel import JSON, Field, Column
from typing import Dict
from app.models.base import BaseModel


class Recipe(BaseModel, table=True):
    text:  Dict = Field(default={}, sa_column=Column(JSON))
    image: str # base64


