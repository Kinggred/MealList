import json
from pathlib import Path
from uuid import UUID

from app.models.diet_ingredient import DietIngredient
from tests.functional.loaders.diets import load_all_diets
from tests.functional.loaders.ingredients import load_all_ingredients

DATA_FILE = Path(__file__).parent.parent / "data" / "diet_ingredients.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_all_diet_ingredients(session) -> list[DietIngredient]:
    diets = load_all_diets(session)
    ingredients = load_all_ingredients(session)

    diet_by_key = {diet.name.lower().replace(" ", "_"): diet for diet in diets}

    ingredient_by_key = {
        ingredient.name.lower().replace(" ", "_"): ingredient
        for ingredient in ingredients
    }

    diet_ingredients = []

    for data in _load_data().values():
        diet_ingredient = DietIngredient(
            id=UUID(data["id"]),
            diet_id=diet_by_key[data["diet"]].id,
            ingredient_id=ingredient_by_key[data["ingredient"]].id,
            created_by=UUID(data["created_by"]),
        )

        diet_ingredients.append(diet_ingredient)

    session.add_all(diet_ingredients)
    session.commit()

    for diet_ingredient in diet_ingredients:
        session.refresh(diet_ingredient)

    return diet_ingredients
