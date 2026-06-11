from tests.constants import TEST_PASSWORD
from tests.loaders.ingredients import load_ingredient, load_all_ingredients
from tests.loaders.recipes import load_recipe, load_all_recipes
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


def recipe_payload(ingredient_id: str, **overrides):
    payload = {
        "name": "Test Recipe",
        "text": {
            "description": "Recipe created from E2E test.",
            "instructions": "Mix and serve.",
        },
        "image": "test-recipe.jpg",
        "ingredients": [
            {
                "ingredient_id": ingredient_id,
                "amount": 100,
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_create_recipe_requires_auth(client, session):
    ingredient = load_ingredient(session, "milk")

    response = client.post(
        "/api/v1/recipes/",
        json=recipe_payload(str(ingredient.id)),
    )

    assert response.status_code == 401


def test_create_recipe(client, session):
    user = load_user(session, "chef_john")
    ingredient = load_ingredient(session, "milk")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/recipes/",
        json=recipe_payload(str(ingredient.id)),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["name"] == "Test Recipe"
    assert body["image"] == "test-recipe.jpg"
    assert body["text"]["description"] == "Recipe created from E2E test."
    assert "id" in body


def test_create_recipe_rejects_missing_ingredients(client, session):
    user = load_user(session, "chef_john")
    headers = login_headers(client, user.email)

    response = client.post(
        "/api/v1/recipes/",
        json={
            "name": "No Ingredients Recipe",
            "text": {"description": "Invalid"},
            "image": "invalid.jpg",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_get_recipes_returns_paginated_items(client, session):
    user = load_user(session, "chef_john")
    load_all_recipes(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/recipes/",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 5
    assert body["page"] == 1
    assert body["size"] == 50
    assert len(body["items"]) == 5


def test_get_recipes_supports_pagination(client, session):
    user = load_user(session, "chef_john")
    load_all_recipes(session)
    headers = login_headers(client, user.email)

    response = client.get(
        "/api/v1/recipes/?page=1&size=2",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 5
    assert body["page"] == 1
    assert body["size"] == 2
    assert len(body["items"]) == 2


def test_get_single_recipe_with_ingredients(client, session):
    user = load_user(session, "chef_john")
    load_all_recipe_ingredients(session)
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == str(recipe.id)
    assert body["name"] == "Scrambled Eggs"
    assert body["total_cost"] > 0
    assert body["total_calories"] > 0
    assert len(body["ingredients"]) == 3

    ingredient_names = {ingredient["name"] for ingredient in body["ingredients"]}

    assert ingredient_names == {"Egg", "Milk", "Butter"}


def test_update_recipe(client, session):
    user = load_user(session, "chef_john")
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    response = client.patch(
        f"/api/v1/recipes/{recipe.id}",
        json={
            "name": "Updated Scrambled Eggs",
            "image": "updated.jpg",
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["id"] == str(recipe.id)
    assert body["name"] == "Updated Scrambled Eggs"
    assert body["image"] == "updated.jpg"


def test_delete_recipe(client, session):
    user = load_user(session, "chef_john")
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    response = client.delete(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_add_ingredient_to_recipe(client, session):
    user = load_user(session, "chef_john")
    recipe = load_recipe(session, "scrambled_eggs")
    ingredient = load_ingredient(session, "sugar")
    headers = login_headers(client, user.email)

    response = client.post(
        f"/api/v1/recipes/{recipe.id}/ingredients",
        json={
            "ingredient_id": str(ingredient.id),
            "amount": 10,
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    body = get_response.json()

    ingredient_names = {ingredient["name"] for ingredient in body["ingredients"]}

    assert "Sugar" in ingredient_names


def test_update_recipe_ingredient_connection(client, session):
    user = load_user(session, "chef_john")
    load_all_recipe_ingredients(session)
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    body = get_response.json()

    milk = next(
        ingredient for ingredient in body["ingredients"] if ingredient["name"] == "Milk"
    )

    response = client.patch(
        f"/api/v1/recipes/{recipe.id}/ingredients/{milk['connection_id']}",
        json={
            "amount": 75,
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    body = get_response.json()

    updated_milk = next(
        ingredient for ingredient in body["ingredients"] if ingredient["name"] == "Milk"
    )

    assert updated_milk["amount"] == 75


def test_delete_recipe_ingredient_connection(client, session):
    user = load_user(session, "chef_john")
    load_all_recipe_ingredients(session)
    recipe = load_recipe(session, "scrambled_eggs")
    headers = login_headers(client, user.email)

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    assert get_response.status_code == 200, get_response.text

    body = get_response.json()

    milk = next(
        ingredient for ingredient in body["ingredients"] if ingredient["name"] == "Milk"
    )

    response = client.delete(
        f"/api/v1/recipes/{recipe.id}/ingredients/{milk['connection_id']}",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    get_response = client.get(
        f"/api/v1/recipes/{recipe.id}",
        headers=headers,
    )

    body = get_response.json()

    ingredient_names = {ingredient["name"] for ingredient in body["ingredients"]}

    assert "Milk" not in ingredient_names
