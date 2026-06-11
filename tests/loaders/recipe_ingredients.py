import json
from pathlib import Path
from uuid import UUID

from app.models.recipe_ingredient import RecipeIngredient
from tests.loaders.ingredients import load_all_ingredients
from tests.loaders.recipes import load_all_recipes

DATA_FILE = Path(__file__).parent.parent / "data" / "recipe_ingredients.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_all_recipe_ingredients(session) -> list[RecipeIngredient]:
    recipes = load_all_recipes(session)
    ingredients = load_all_ingredients(session)

    recipe_by_key = {
        recipe.name.lower().replace(" ", "_"): recipe for recipe in recipes
    }

    ingredient_by_key = {
        ingredient.name.lower().replace(" ", "_"): ingredient
        for ingredient in ingredients
    }

    recipe_ingredients = []

    for data in _load_data().values():
        recipe_ingredient = RecipeIngredient(
            id=UUID(data["id"]),
            recipe_id=recipe_by_key[data["recipe"]].id,
            ingredient_id=ingredient_by_key[data["ingredient"]].id,
            amount=data["amount"],
            created_by=UUID(data["created_by"]),
        )

        recipe_ingredients.append(recipe_ingredient)

    session.add_all(recipe_ingredients)
    session.commit()

    for recipe_ingredient in recipe_ingredients:
        session.refresh(recipe_ingredient)

    return recipe_ingredients
