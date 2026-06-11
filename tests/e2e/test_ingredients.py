from tests.constants import TEST_PASSWORD
from tests.loaders.ingredients import load_all_ingredients, load_ingredient
from tests.loaders.users import load_user


def auth_headers(client, session):
    user = load_user(session, "chef_john")

    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def ingredient_payload(**overrides):
    payload = {
        "name": "Cucumber",
        "calories": 150,
        "cost": 2.5,
        "amount_per_cost": 1,
        "unit_of_measurement": "p",
        "animal_produced": False,
        "animal_derived": False,
    }
    payload.update(overrides)
    return payload


def test_create_ingredient_requires_auth(client):
    response = client.post(
        "/api/v1/ingredients/",
        json=ingredient_payload(),
    )

    assert response.status_code == 401


def test_create_ingredient(client, session):
    headers = auth_headers(client, session)

    response = client.post(
        "/api/v1/ingredients/",
        json=ingredient_payload(),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Cucumber"
    assert body["calories"] == 150
    assert body["cost"] == 2.5
    assert body["amount_per_cost"] == 1
    assert body["unit_of_measurement"] == "p"
    assert body["animal_produced"] is False
    assert body["animal_derived"] is False


def test_create_ingredient_rejects_invalid_unit(client, session):
    headers = auth_headers(client, session)

    response = client.post(
        "/api/v1/ingredients/",
        json=ingredient_payload(unit_of_measurement="kg"),
        headers=headers,
    )

    assert response.status_code == 422


def test_get_ingredients_returns_paginated_items(client, session):
    headers = auth_headers(client, session)
    load_all_ingredients(session)

    response = client.get(
        "/api/v1/ingredients/",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 16
    assert body["page"] == 1
    assert body["size"] == 50
    assert len(body["items"]) == 16


def test_get_ingredients_supports_pagination(client, session):
    headers = auth_headers(client, session)
    load_all_ingredients(session)

    response = client.get(
        "/api/v1/ingredients/?page=1&size=5",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 16
    assert body["page"] == 1
    assert body["size"] == 5
    assert len(body["items"]) == 5


def test_get_single_ingredient(client, session):
    headers = auth_headers(client, session)
    ingredient = load_ingredient(session, "milk")

    response = client.get(
        f"/api/v1/ingredients/{ingredient.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(ingredient.id)
    assert body["name"] == "Milk"
    assert body["unit_of_measurement"] == "ml"
    assert "alternatives" in body
    assert "contains" in body


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


from app.crud.ingredient import ingredient_crud
from app.api.auth import get_current_user


def test_update_ingredient(client, session):
    user = load_user(session, "chef_john")
    ingredient = load_ingredient(session, "milk")

    assert ingredient.created_by == user.id

    # direct DB/CRUD checks
    assert ingredient_crud.model.__name__ == "Ingredient"
    assert ingredient_crud.get(session, ingredient.id) is not None
    assert ingredient_crud.safe_get(session, ingredient.id).id == ingredient.id

    headers = login_headers(client, user.email)

    response = client.patch(
        f"/api/v1/ingredients/{ingredient.id}",
        json={
            "name": "Updated Milk",
            "cost": 5.0,
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text


def test_delete_ingredient(client, session):
    user = load_user(session, "chef_john")
    ingredient = load_ingredient(session, "milk")
    headers = login_headers(client, user.email)

    response = client.delete(
        f"/api/v1/ingredients/{ingredient.id}",
        headers=headers,
    )

    assert response.status_code == 200

    session.expire_all()

    get_response = client.get(
        f"/api/v1/ingredients/{ingredient.id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_create_ingredient_tie(client, session):
    headers = auth_headers(client, session)
    butter = load_ingredient(session, "butter")
    milk = load_ingredient(session, "milk")

    response = client.post(
        f"/api/v1/ingredients/ties/{butter.id}",
        json={
            "contained_id": str(milk.id),
            "is_alternative": False,
            "include_in_count": False,
        },
        headers=headers,
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/api/v1/ingredients/{butter.id}",
        headers=headers,
    )

    assert get_response.status_code == 200

    body = get_response.json()

    assert body["id"] == str(butter.id)
    assert body["contains"]["uncounted"][0]["id"] == str(milk.id)
