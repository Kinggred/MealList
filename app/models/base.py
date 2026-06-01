from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel, func


def generate_auto_model_name(model: str, create_date: datetime):
    return f"New {model} {create_date.strftime('%Y-%m-%d')}"


class BaseModel(SQLModel):
    id: UUID = Field(
        primary_key=True,
        sa_column_kwargs={
            "server_default": "uuid_generate_v4()",
        },
    )
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)
    enabled: bool = True
