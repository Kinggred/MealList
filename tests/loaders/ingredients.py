from pathlib import Path

from app.models.ingridient import Ingredient
from tests.loaders.base import load_json, load_many, load_single
from tests.loaders.users import load_user

DATA_FILE = Path(__file__).parent.parent / "data" / "ingredients.json"


def load_ingredient(session, name: str) -> Ingredient:
    load_user(session, "chef_john")
    data = load_json(DATA_FILE)

    return load_single(
        session=session,
        model=Ingredient,
        data=data[name],
        builder=Ingredient.model_validate,
    )


def load_all_ingredients(session) -> list[Ingredient]:
    load_user(session, "chef_john")
    return load_many(
        session=session,
        model=Ingredient,
        data=load_json(DATA_FILE),
        builder=Ingredient.model_validate,
    )
