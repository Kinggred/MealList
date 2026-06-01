from functools import lru_cache
from os import environ

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


if not environ.get("POSTGRES_USER"):
    from dotenv import load_dotenv

    load_dotenv(".env.local")


class Settings(BaseSettings):
    DEBUG: bool = Field(env="DEBUG", default=False)
    # DB Connection
    POSTGRES_HOST: str = Field(env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(env="POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = Field(env="POSTGRES_DB")
    POSTGRES_USER: str = Field(env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    POSTGRES_DSN: PostgresDsn = Field(default="")
    # Authorization
    IDP_ALLOWED_ISSUERS: str = Field(env="IDP_ALLOWED_ISSUERS", default="")
    IDP_AUDIENCE: str = Field(env="IDP_AUDIENCE", default="")
    ALLOWED_CORS_ORIGINS: str = Field(env="ALLOWED_CORS_ORIGINS", default="*")

    @validator("POSTGRES_DSN", pre=True)
    def set_postgres_dsn(cls, current_value, values):
        if current_value:
            return current_value
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
