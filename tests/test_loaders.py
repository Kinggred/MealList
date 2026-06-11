from uuid import UUID

from tests.loaders.diet_ingredients import load_all_diet_ingredients
from tests.loaders.diets import load_diet, load_all_diets
from tests.loaders.ingredient_ties import load_all_ingredient_ties
from tests.loaders.meal_dish import load_all_meal_dishes
from tests.loaders.meals import load_meal, load_all_meals
from tests.loaders.recipe_ingredients import load_all_recipe_ingredients
from tests.loaders.recipes import load_recipe, load_all_recipes
from tests.loaders.users import load_user, load_all_users
from tests.loaders.ingredients import load_all_ingredients, load_ingredient


def test_load_single_user(session):
    user = load_user(session, "chef_john")

    assert user.email == "john@meallist.local"


def test_load_all_users(session):
    users = load_all_users(session)

    assert len(users) == 5


def test_load_single_ingredient(session):
    load_user(session, "chef_john")
    ingredient = load_ingredient(session, "milk")

    assert ingredient.name == "Milk"
    assert ingredient.unit_of_measurement == "ml"
    assert ingredient.amount_per_cost == 1000


def test_load_all_ingredients(session):
    load_user(session, "chef_john")
    ingredients = load_all_ingredients(session)

    assert len(ingredients) == 16


def test_load_all_ingredient_ties(session):
    load_user(session, "chef_john")

    ties = load_all_ingredient_ties(session)

    assert len(ties) == 5
    assert all(isinstance(tie.id, UUID) for tie in ties)
    assert all(isinstance(tie.ingredient_id, UUID) for tie in ties)
    assert all(isinstance(tie.contained_id, UUID) for tie in ties)


def test_load_single_diet(session):
    load_user(session, "chef_john")

    diet = load_diet(session, "vegetarian")

    assert isinstance(diet.id, UUID)
    assert diet.name == "Vegetarian"
    assert "description" in diet.content


def test_load_all_diets(session):
    load_user(session, "chef_john")

    diets = load_all_diets(session)

    assert len(diets) == 2
    assert {diet.name for diet in diets} == {"Vegetarian", "Vegan"}


def test_load_all_diet_ingredients(session):
    load_user(session, "chef_john")

    diet_ingredients = load_all_diet_ingredients(session)

    assert len(diet_ingredients) == 6
    assert all(isinstance(item.id, UUID) for item in diet_ingredients)
    assert all(isinstance(item.diet_id, UUID) for item in diet_ingredients)
    assert all(isinstance(item.ingredient_id, UUID) for item in diet_ingredients)


def test_load_single_recipe(session):
    load_user(session, "chef_john")

    recipe = load_recipe(session, "scrambled_eggs")

    assert isinstance(recipe.id, UUID)
    assert recipe.name == "Scrambled Eggs"
    assert recipe.text["description"] == "Classic scrambled eggs with milk and butter."


def test_load_all_recipes(session):
    load_user(session, "chef_john")

    recipes = load_all_recipes(session)

    assert len(recipes) == 5
    assert {recipe.name for recipe in recipes} == {
        "Scrambled Eggs",
        "Chicken Rice",
        "Cheese Sandwich",
        "Tomato Sandwich",
        "Potato Pancakes",
    }


def test_load_all_recipe_ingredients(session):
    load_user(session, "chef_john")

    recipe_ingredients = load_all_recipe_ingredients(session)

    assert len(recipe_ingredients) == 18
    assert all(isinstance(item.id, UUID) for item in recipe_ingredients)
    assert all(isinstance(item.recipe_id, UUID) for item in recipe_ingredients)
    assert all(isinstance(item.ingredient_id, UUID) for item in recipe_ingredients)


def test_load_single_meal(session):
    load_user(session, "chef_john")

    meal = load_meal(session, "monday_breakfast")

    assert isinstance(meal.id, UUID)
    assert meal.name == "Monday Breakfast"
    assert meal.date.isoformat() == "2026-06-01T08:00:00"


def test_load_all_meals(session):
    load_user(session, "chef_john")

    meals = load_all_meals(session)

    assert len(meals) == 5
    assert {meal.name for meal in meals} == {
        "Monday Breakfast",
        "Monday Lunch",
        "Monday Dinner",
        "Tuesday Breakfast",
        "Tuesday Lunch",
    }


def test_load_all_meal_dishes(session):
    load_user(session, "chef_john")

    meal_dishes = load_all_meal_dishes(session)

    assert len(meal_dishes) == 6
    assert all(isinstance(item.id, UUID) for item in meal_dishes)
    assert all(isinstance(item.meal_id, UUID) for item in meal_dishes)
    assert all(isinstance(item.recipe_id, UUID) for item in meal_dishes)
