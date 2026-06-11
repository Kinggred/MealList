import json
from pathlib import Path
from uuid import UUID

from app.models.meal_dish import MealDish
from tests.functional.loaders.meals import load_all_meals
from tests.functional.loaders.recipes import load_all_recipes

DATA_FILE = Path(__file__).parent.parent / "data" / "meal_dishes.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_all_meal_dishes(session) -> list[MealDish]:
    meals = load_all_meals(session)
    recipes = load_all_recipes(session)

    meal_by_key = {meal.name.lower().replace(" ", "_"): meal for meal in meals}

    recipe_by_key = {
        recipe.name.lower().replace(" ", "_"): recipe for recipe in recipes
    }

    meal_dishes = []

    for data in _load_data().values():
        meal_dish = MealDish(
            id=UUID(data["id"]),
            meal_id=meal_by_key[data["meal"]].id,
            recipe_id=recipe_by_key[data["recipe"]].id,
            full_portions=data["full_portions"],
            half_portions=data["half_portions"],
            created_by=UUID(data["created_by"]),
        )

        meal_dishes.append(meal_dish)

    session.add_all(meal_dishes)
    session.commit()

    for meal_dish in meal_dishes:
        session.refresh(meal_dish)

    return meal_dishes
