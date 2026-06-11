import json
from pathlib import Path
from uuid import UUID

from app.models.recipe import Recipe

DATA_FILE = Path(__file__).parent.parent / "data" / "recipes.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_recipe(session, name: str) -> Recipe:
    data = _load_data()[name]

    recipe = Recipe(
        id=UUID(data["id"]),
        name=data["name"],
        text=data["text"],
        image=data["image"],
        created_by=UUID(data["created_by"]),
    )

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe


def load_all_recipes(session) -> list[Recipe]:
    recipes = []

    for data in _load_data().values():
        recipe_id = UUID(data["id"])

        existing = session.get(Recipe, recipe_id)
        if existing is not None:
            recipes.append(existing)
            continue

        recipe = Recipe(
            id=recipe_id,
            name=data["name"],
            text=data["text"],
            image=data["image"],
            created_by=UUID(data["created_by"]),
        )
        session.add(recipe)
        recipes.append(recipe)

    session.commit()

    for recipe in recipes:
        session.refresh(recipe)

    return recipes
