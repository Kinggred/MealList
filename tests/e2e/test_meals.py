from tests.constants import TEST_PASSWORD
from tests.loaders.meals import load_meal, load_all_meals
from tests.loaders.recipes import load_recipe
from tests.loaders.meal_dish import load_all_meal_dishes
from tests.loaders.recipe_ingredients import load_all_recipe_ingredients
from tests.loaders.users import load_user


def login_headers(client, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


def meal_payload(recipe_id: str, **overrides):
    payload = {
        "name": "Test Meal",
        "date": "2026-06-03T12:00:00",
        "dishes": [
            {
                "recipe_id": recipe_id,
                "full_portions": 2,
                "half_portions": 1,
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_create_meal_requires_auth(client, session):
    recipe = load_recipe(session, "scrambled_eggs")

    response = client.post(
        "/api/v1/meals/",
        json=meal_payload(str(recipe.id)),
    )

    assert response.status_code == 401


def test_create_meal(client, session):
    user = load_user(session, "chef_john")
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/meals/",
        json=meal_payload(str(recipe.id)),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["name"] == "Test Meal"
    assert body["date"].startswith("2026-06-03T12:00:00")
    assert "id" in body


def test_create_meal_rejects_missing_dishes(client, session):
    user = load_user(session, "chef_john")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/meals/",
        json={
            "name": "Invalid Meal",
            "date": "2026-06-03T12:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_get_meals_returns_range_results(client, session):
    user = load_user(session, "chef_john")
    load_all_meals(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/?date_from=2026-06-01&date_to=2026-06-02",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body["results"]) == 5

    names = {meal["name"] for meal in body["results"]}

    assert names == {
        "Monday Breakfast",
        "Monday Lunch",
        "Monday Dinner",
        "Tuesday Breakfast",
        "Tuesday Lunch",
    }


def test_get_single_meal_with_dishes(client, session):
    user = load_user(session, "chef_john")
    load_all_meal_dishes(session)
    meal = load_meal(session, "monday_breakfast")
    headers = login_headers(client, user.email)

    response = client.get(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["name"] == "Monday Breakfast"
    assert body["date"].startswith("2026-06-01T08:00:00")
    assert len(body["dishes"]) == 1

    dish = body["dishes"][0]

    assert dish["recipe"]["name"] == "Scrambled Eggs"
    assert dish["full_portions"] == 2
    assert dish["half_portions"] == 1
    assert "connection_id" in dish


def test_update_meal(client, session):
    user = load_user(session, "chef_john")
    meal = load_meal(session, "monday_breakfast")
    headers = login_headers(client, user.email)

    response = client.patch(
        f"/api/v1/meals/{meal.id}",
        json={
            "name": "Updated Breakfast",
            "date": "2026-06-01T09:00:00",
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == str(meal.id)
    assert body["name"] == "Updated Breakfast"
    assert body["date"].startswith("2026-06-01T09:00:00")


def test_delete_meal(client, session):
    user = load_user(session, "chef_john")
    meal = load_meal(session, "monday_breakfast")
    headers = login_headers(client, user.email)

    response = client.delete(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    session.expire_all()

    get_response = client.get(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_add_dish_to_meal(client, session):
    user = load_user(session, "chef_john")
    meal = load_meal(session, "monday_breakfast")
    recipe = load_recipe(session, "tomato_sandwich")
    headers = login_headers(client, user.email)

    response = client.post(
        f"/api/v1/meals/{meal.id}/dishes",
        json={
            "recipe_id": str(recipe.id),
            "full_portions": 1,
            "half_portions": 0,
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["meal_id"] == str(meal.id)
    assert body["recipe_id"] == str(recipe.id)
    assert body["full_portions"] == 1
    assert body["half_portions"] == 0


def test_update_dish_connection(client, session):
    user = load_user(session, "chef_john")
    load_all_meal_dishes(session)
    meal = load_meal(session, "monday_breakfast")
    headers = login_headers(client, user.email)

    get_response = client.get(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    dish = get_response.json()["dishes"][0]

    response = client.patch(
        f"/api/v1/meals/{meal.id}/dishes/{dish['connection_id']}",
        json={
            "full_portions": 4,
            "half_portions": 2,
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == dish["connection_id"]
    assert body["full_portions"] == 4
    assert body["half_portions"] == 2


def test_delete_dish_connection(client, session):
    user = load_user(session, "chef_john")
    load_all_meal_dishes(session)
    meal = load_meal(session, "monday_breakfast")
    headers = login_headers(client, user.email)

    get_response = client.get(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    dish = get_response.json()["dishes"][0]

    response = client.delete(
        f"/api/v1/meals/{meal.id}/dishes/{dish['connection_id']}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    session.expire_all()

    get_response = client.get(
        f"/api/v1/meals/{meal.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    assert get_response.json()["dishes"] == []


def test_get_shopping_list_endpoint(client, session):
    user = load_user(session, "chef_john")
    load_all_recipe_ingredients(session)
    load_all_meal_dishes(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/shopping_list?date_from=2026-06-01&date_to=2026-06-02",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["date_from"] == "2026-06-01"
    assert body["date_to"] == "2026-06-02"
    assert len(body["ingredient_list"]) > 0

    items_by_name = {item["name"]: item for item in body["ingredient_list"]}

    assert items_by_name["Egg"]["exact_amount"] == 18
    assert items_by_name["Milk"]["exact_amount"] == 300
    assert items_by_name["Butter"]["exact_amount"] == 150
