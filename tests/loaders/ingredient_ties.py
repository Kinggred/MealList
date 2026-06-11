from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "ingredient_ties.json"


import json
from pathlib import Path
from uuid import UUID

from app.models.ingredient_self_reference import IngredientSelfReference
from tests.loaders.ingredients import load_all_ingredients

DATA_FILE = Path(__file__).parent.parent / "data" / "ingredient_ties.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_all_ingredient_ties(session) -> list[IngredientSelfReference]:
    ingredients = load_all_ingredients(session)

    ingredient_by_key = {
        ingredient.name.lower().replace(" ", "_"): ingredient
        for ingredient in ingredients
    }

    ties = []

    for tie_data in _load_data().values():
        tie = IngredientSelfReference(
            id=UUID(tie_data["id"]),
            created_by=UUID(tie_data["created_by"]),
            ingredient_id=ingredient_by_key[tie_data["ingredient"]].id,
            contained_id=ingredient_by_key[tie_data["contained"]].id,
            is_alternative=tie_data["is_alternative"],
            include_in_count=tie_data["include_in_count"],
        )
        ties.append(tie)

    session.add_all(ties)
    session.commit()

    for tie in ties:
        session.refresh(tie)

    return ties
