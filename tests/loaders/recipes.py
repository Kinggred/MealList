from pathlib import Path

from app.models.recipe import Recipe
from tests.loaders.base import load_json, load_many, load_single
from tests.loaders.users import load_user

DATA_FILE = Path(__file__).parent.parent / "data" / "recipes.json"


def build_recipe(data: dict) -> Recipe:
    return Recipe.model_validate(data)


def load_recipe(session, name: str) -> Recipe:
    load_user(session, "chef_john")
    return load_single(
        session=session,
        model=Recipe,
        data=load_json(DATA_FILE)[name],
        builder=build_recipe,
    )


def load_all_recipes(session) -> list[Recipe]:
    load_user(session, "chef_john")
    return load_many(
        session=session,
        model=Recipe,
        data=load_json(DATA_FILE),
        builder=build_recipe,
    )
