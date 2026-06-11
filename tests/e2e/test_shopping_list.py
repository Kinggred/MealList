from tests.constants import TEST_PASSWORD
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


def load_shopping_list_e2e_dataset(session):
    user = load_user(session, "chef_john")

    # This loads the dependency graph:
    # users -> ingredients -> recipes -> recipe ingredients
    # users -> meals -> recipes -> meal dishes
    load_all_recipe_ingredients(session)
    load_all_meal_dishes(session)

    return user


def test_get_shopping_list_requires_auth(client):
    response = client.get(
        "/api/v1/meals/shopping_list?date_from=2026-06-01&date_to=2026-06-02",
    )

    assert response.status_code == 401


def test_get_shopping_list_for_two_days(client, session):
    user = load_shopping_list_e2e_dataset(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/shopping_list?date_from=2026-06-01&date_to=2026-06-02",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["date_from"] == "2026-06-01"
    assert body["date_to"] == "2026-06-02"

    items_by_name = {item["name"]: item for item in body["ingredient_list"]}

    assert items_by_name["Egg"]["exact_amount"] == 18
    assert items_by_name["Egg"]["amount"] == 18
    assert items_by_name["Egg"]["estimated_cost"] == 18

    assert items_by_name["Milk"]["exact_amount"] == 300
    assert items_by_name["Milk"]["amount"] == 1000
    assert items_by_name["Milk"]["estimated_cost"] == 1.35

    assert items_by_name["Butter"]["exact_amount"] == 150
    assert items_by_name["Butter"]["amount"] == 200
    assert items_by_name["Butter"]["estimated_cost"] == 6.0

    assert items_by_name["Chicken Breast"]["exact_amount"] == 600
    assert items_by_name["Chicken Breast"]["amount"] == 1000
    assert items_by_name["Rice"]["exact_amount"] == 300
    assert items_by_name["Rice"]["amount"] == 1000


def test_get_shopping_list_for_single_day(client, session):
    user = load_shopping_list_e2e_dataset(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/shopping_list?date_from=2026-06-01&date_to=2026-06-01",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["date_from"] == "2026-06-01"
    assert body["date_to"] == "2026-06-01"

    items_by_name = {item["name"]: item for item in body["ingredient_list"]}

    assert items_by_name["Egg"]["exact_amount"] == 9
    assert items_by_name["Egg"]["amount"] == 9

    assert items_by_name["Milk"]["exact_amount"] == 150
    assert items_by_name["Milk"]["amount"] == 1000

    assert items_by_name["Butter"]["exact_amount"] == 90
    assert items_by_name["Butter"]["amount"] == 200

    assert items_by_name["Chicken Breast"]["exact_amount"] == 600
    assert items_by_name["Chicken Breast"]["amount"] == 1000

    assert items_by_name["Rice"]["exact_amount"] == 300
    assert items_by_name["Rice"]["amount"] == 1000


def test_get_shopping_list_for_empty_range(client, session):
    user = load_shopping_list_e2e_dataset(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/shopping_list?date_from=2026-07-01&date_to=2026-07-02",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["date_from"] == "2026-07-01"
    assert body["date_to"] == "2026-07-02"
    assert body["ingredient_list"] == []


def test_get_shopping_list_rejects_invalid_date(client, session):
    user = load_user(session, "chef_john")
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/meals/shopping_list?date_from=not-a-date&date_to=2026-06-02",
        headers=headers,
    )

    assert response.status_code == 422
