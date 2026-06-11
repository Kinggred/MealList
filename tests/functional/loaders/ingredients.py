import json
from pathlib import Path

from app.models.ingridient import Ingredient

DATA_FILE = Path(__file__).parent.parent / "data" / "ingredients.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_ingredient(session, name: str) -> Ingredient:
    data = _load_data()[name]

    ingredient = Ingredient.model_validate(data)

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient


def load_all_ingredients(session) -> list[Ingredient]:
    data = _load_data()

    ingredients = [
        Ingredient.model_validate(ingredient_data) for ingredient_data in data.values()
    ]

    session.add_all(ingredients)
    session.commit()

    for ingredient in ingredients:
        session.refresh(ingredient)

    return ingredients
