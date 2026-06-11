from pathlib import Path

from app.models.meal import Meal
from tests.loaders.base import load_json, load_many, load_single
from tests.loaders.users import load_user

DATA_FILE = Path(__file__).parent.parent / "data" / "meals.json"


def build_meal(data: dict) -> Meal:
    return Meal.model_validate(data)


def load_meal(session, name: str) -> Meal:
    load_user(session, "chef_john")
    return load_single(
        session=session,
        model=Meal,
        data=load_json(DATA_FILE)[name],
        builder=build_meal,
    )


def load_all_meals(session) -> list[Meal]:
    load_user(session, "chef_john")
    return load_many(
        session=session,
        model=Meal,
        data=load_json(DATA_FILE),
        builder=build_meal,
    )
