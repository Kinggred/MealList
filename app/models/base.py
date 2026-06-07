from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel, func, text


class BaseModel(SQLModel):
    id: UUID = Field(
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("uuid_generate_v4()"),
        },
    )
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)
    enabled: bool = True
