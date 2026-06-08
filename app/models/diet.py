from sqlmodel import JSON, Field, Column
from typing import Dict
from app.models.base import BaseModel


class Diet(BaseModel, table=True):
    name: str
    content: Dict = Field(default={}, sa_column=Column(JSON))
