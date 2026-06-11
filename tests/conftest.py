from dotenv import load_dotenv

load_dotenv(".env.test")

from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.api.database import get_session
from app.api.main import app

# Import table models so SQLModel.metadata contains them.
from app.models.diet import Diet  # noqa: F401
from app.models.diet_ingredient import DietIngredient  # noqa: F401
from app.models.ingredient_self_reference import IngredientSelfReference  # noqa: F401
from app.models.ingridient import Ingredient  # noqa: F401
from app.models.meal import Meal  # noqa: F401
from app.models.meal_dish import MealDish  # noqa: F401
from app.models.recipe import Recipe  # noqa: F401
from app.models.recipe_ingredient import RecipeIngredient  # noqa: F401
from app.models.user import User  # noqa: F401


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def make_uuid():
    def _make_uuid() -> UUID:
        return uuid4()

    return _make_uuid
