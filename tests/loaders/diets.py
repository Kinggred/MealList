from pathlib import Path

from app.models.diet import Diet
from tests.loaders.base import load_json, load_many, load_single
from tests.loaders.users import load_user

DATA_FILE = Path(__file__).parent.parent / "data" / "diets.json"


def build_diet(data: dict) -> Diet:
    return Diet.model_validate(data)


def load_diet(session, name: str) -> Diet:
    load_user(session, "chef_john")
    return load_single(
        session=session,
        model=Diet,
        data=load_json(DATA_FILE)[name],
        builder=build_diet,
    )


def load_all_diets(session) -> list[Diet]:
    load_user(session, "chef_john")
    return load_many(
        session=session,
        model=Diet,
        data=load_json(DATA_FILE),
        builder=build_diet,
    )
