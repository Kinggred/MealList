from tests.constants import TEST_PASSWORD
from tests.loaders.diets import load_all_diets, load_diet
from tests.loaders.diet_ingredients import load_all_diet_ingredients
from tests.loaders.ingredients import load_ingredient
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


def diet_payload(ingredient_id: str, **overrides):
    payload = {
        "name": "Test Diet",
        "content": {
            "description": "Diet created from E2E test.",
        },
        "ingredients": [ingredient_id],
    }
    payload.update(overrides)
    return payload


def test_create_diet_requires_auth(client, session):
    user = load_user(session, "chef_john")
    ingredient = load_ingredient(session, "rice")

    response = client.post(
        "/api/v1/diets/",
        json=diet_payload(str(ingredient.id)),
    )

    assert response.status_code == 401


def test_create_diet(client, session):
    user = load_user(session, "chef_john")
    ingredient = load_ingredient(session, "rice")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/diets/",
        json=diet_payload(str(ingredient.id)),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["name"] == "Test Diet"
    assert body["content"]["description"] == "Diet created from E2E test."
    assert "id" in body


def test_create_diet_rejects_missing_ingredients(client, session):
    user = load_user(session, "chef_john")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/diets/",
        json={
            "name": "Invalid Diet",
            "content": {},
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_get_diets_returns_paginated_items(client, session):
    user = load_user(session, "chef_john")
    load_all_diets(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/diets/",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["total"] == 2
    assert body["page"] == 1
    assert body["size"] == 50
    assert len(body["items"]) == 2


def test_get_diets_supports_pagination(client, session):
    user = load_user(session, "chef_john")
    load_all_diets(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/diets/?page=1&size=1",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["total"] == 2
    assert body["page"] == 1
    assert body["size"] == 1
    assert len(body["items"]) == 1


def test_get_single_diet_with_ingredients(client, session):
    user = load_user(session, "chef_john")
    load_all_diet_ingredients(session)
    diet = load_diet(session, "vegan")
    headers = login_headers(client, user.email)

    response = client.get(
        f"/api/v1/diets/{diet.id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == str(diet.id)
    assert body["name"] == "Vegan"
    assert "ingredients" in body
    assert len(body["ingredients"]) > 0

    ingredient_names = {ingredient["name"] for ingredient in body["ingredients"]}

    assert "Rice" in ingredient_names


def test_update_diet(client, session):
    user = load_user(session, "chef_john")
    diet = load_diet(session, "vegetarian")
    headers = login_headers(client, user.email)

    response = client.patch(
        f"/api/v1/diets/{diet.id}",
        json={
            "name": "Updated Vegetarian",
            "content": {
                "description": "Updated description.",
            },
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == str(diet.id)
    assert body["name"] == "Updated Vegetarian"


def test_delete_diet(client, session):
    user = load_user(session, "chef_john")
    diet = load_diet(session, "vegetarian")
    headers = login_headers(client, user.email)

    response = client.delete(
        f"/api/v1/diets/{diet.id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    session.expire_all()

    get_response = client.get(
        f"/api/v1/diets/{diet.id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_update_diet_ingredients_add_and_remove(client, session):
    user = load_user(session, "chef_john")
    load_all_diet_ingredients(session)

    diet = load_diet(session, "vegetarian")
    rice = load_ingredient(session, "rice")
    milk = load_ingredient(session, "milk")

    headers = login_headers(client, user.email)

    add_response = client.patch(
        f"/api/v1/diets/{diet.id}/ingredients",
        json={
            "add": [str(rice.id)],
            "remove": [str(milk.id)],
        },
        headers=headers,
    )

    assert add_response.status_code == 200, add_response.text

    session.expire_all()

    get_response = client.get(
        f"/api/v1/diets/{diet.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    body = get_response.json()

    ingredient_names = {ingredient["name"] for ingredient in body["ingredients"]}

    assert "Rice" in ingredient_names
    assert "Milk" not in ingredient_names
