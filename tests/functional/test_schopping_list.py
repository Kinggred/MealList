from datetime import date, datetime, time

from app.crud.ingredient import ingredient_crud
from app.crud.meal import meal_crud
from app.crud.meal_dish import meal_dish_crud
from app.crud.recipe_ingredient import recipe_ingredient_crud
from tests.loaders.meal_dish import load_all_meal_dishes
from tests.loaders.recipe_ingredients import load_all_recipe_ingredients
from tests.loaders.users import load_user

"""
 These tests are not exactly functional ... 
 those would require a lots of mocks.
 Instead we test removing Fastapi client and Pydantics validation of requests and such
"""


def load_shopping_list_dataset(session):
    user = load_user(session, "chef_john")

    # These two loaders should together load:
    # meals, meal dishes, recipes, ingredients, recipe ingredients.
    load_all_meal_dishes(session)
    load_all_recipe_ingredients(session)

    return user


def get_range(date_from: date, date_to: date):
    return (
        datetime.combine(date_from, time.min),
        datetime.combine(date_to, time.max),
    )


def test_get_meals_in_range_returns_expected_meals(session):
    user = load_shopping_list_dataset(session)

    start_dt, end_dt = get_range(
        date(2026, 6, 1),
        date(2026, 6, 1),
    )

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    assert len(meals.results) == 3
    assert {meal.name for meal in meals.results} == {
        "Monday Breakfast",
        "Monday Lunch",
        "Monday Dinner",
    }


def test_get_dishes_from_meal_list_aggregates_by_recipe(session):
    user = load_shopping_list_dataset(session)

    start_dt, end_dt = get_range(
        date(2026, 6, 1),
        date(2026, 6, 2),
    )

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    meal_ids = [meal.id for meal in meals.results]

    dishes = meal_dish_crud.get_dishes_from_meal_list(
        db=session,
        meal_ids=meal_ids,
    )

    assert len(dishes) == 5

    recipe_ids = {dish.recipe_id for dish in dishes}

    assert len(recipe_ids) == 5


def test_recipe_ingredient_calculations_have_expected_items(session):
    user = load_shopping_list_dataset(session)

    start_dt, end_dt = get_range(
        date(2026, 6, 1),
        date(2026, 6, 2),
    )

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    dishes = meal_dish_crud.get_dishes_from_meal_list(
        db=session,
        meal_ids=[meal.id for meal in meals.results],
    )

    calculations = recipe_ingredient_crud.get_ingredient_calculations_from_dishes(
        session,
        dishes=dishes,
    )

    assert len(calculations) > 0

    calculation_ids = {calculation.ingredient_id for calculation in calculations}

    assert len(calculation_ids) == len(calculations)


def test_build_shopping_list_returns_expected_dates_and_items(session):
    user = load_shopping_list_dataset(session)

    date_from = date(2026, 6, 1)
    date_to = date(2026, 6, 2)
    start_dt, end_dt = get_range(date_from, date_to)

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    dishes = meal_dish_crud.get_dishes_from_meal_list(
        db=session,
        meal_ids=[meal.id for meal in meals.results],
    )

    calculations = recipe_ingredient_crud.get_ingredient_calculations_from_dishes(
        session,
        dishes=dishes,
    )

    shopping_list = ingredient_crud.build_shopping_list(
        session,
        date_from=date_from,
        date_to=date_to,
        calculations=calculations,
    )

    assert shopping_list.date_from == date_from
    assert shopping_list.date_to == date_to
    assert len(shopping_list.ingredient_list) > 0


def test_full_shopping_list_for_two_days_has_expected_amounts(session):
    user = load_shopping_list_dataset(session)

    date_from = date(2026, 6, 1)
    date_to = date(2026, 6, 2)
    start_dt, end_dt = get_range(date_from, date_to)

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    dishes = meal_dish_crud.get_dishes_from_meal_list(
        db=session,
        meal_ids=[meal.id for meal in meals.results],
    )

    calculations = recipe_ingredient_crud.get_ingredient_calculations_from_dishes(
        session,
        dishes=dishes,
    )

    shopping_list = ingredient_crud.build_shopping_list(
        session,
        date_from=date_from,
        date_to=date_to,
        calculations=calculations,
    )

    items_by_name = {item.name: item for item in shopping_list.ingredient_list}

    assert items_by_name["Egg"].exact_amount == 18
    assert items_by_name["Milk"].exact_amount == 300
    assert items_by_name["Butter"].exact_amount == 150
    assert items_by_name["Chicken Breast"].exact_amount == 600
    assert items_by_name["Rice"].exact_amount == 300


def test_full_shopping_list_for_single_day_has_expected_amounts(session):
    user = load_shopping_list_dataset(session)

    date_from = date(2026, 6, 1)
    date_to = date(2026, 6, 1)
    start_dt, end_dt = get_range(date_from, date_to)

    meals = meal_crud.get_meals_in_range(
        db=session,
        user=user,
        start_date=start_dt,
        end_date=end_dt,
    )

    dishes = meal_dish_crud.get_dishes_from_meal_list(
        db=session,
        meal_ids=[meal.id for meal in meals.results],
    )

    calculations = recipe_ingredient_crud.get_ingredient_calculations_from_dishes(
        session,
        dishes=dishes,
    )

    shopping_list = ingredient_crud.build_shopping_list(
        session,
        date_from=date_from,
        date_to=date_to,
        calculations=calculations,
    )

    items_by_name = {item.name: item for item in shopping_list.ingredient_list}

    # Monday Breakfast:
    # Scrambled Eggs: 2 full + ceil(1 / 2) = 3 portions
    assert items_by_name["Egg"].exact_amount == 9
    assert items_by_name["Milk"].exact_amount == 150

    # Scrambled Eggs butter: 20g * 3 = 60g
    # Cheese Sandwich butter:
    # Monday Dinner: 1 full + ceil(2 / 2) = 2 portions
    # 15g * 2 = 30g
    # Total butter = 90g
    assert items_by_name["Butter"].exact_amount == 90

    # Monday Lunch:
    # Chicken Rice: 3 portions
    assert items_by_name["Chicken Breast"].exact_amount == 600
    assert items_by_name["Rice"].exact_amount == 300
