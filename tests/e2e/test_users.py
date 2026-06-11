from tests.constants import TEST_PASSWORD
from tests.loaders.users import load_user


def login(client, email: str, password: str = TEST_PASSWORD) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_user_returns_created_user(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "username": "new_user",
            "email": "new_user@meallist.local",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "id" in body
    assert body["username"] == "new_user"
    assert body["email"] == "new_user@meallist.local"
    assert "password" not in body
    assert "password_hash" not in body


def test_create_user_with_duplicate_email_fails(client, session):
    user = load_user(session, "chef_john")

    response = client.post(
        "/api/v1/users/",
        json={
            "username": "duplicate",
            "email": user.email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 400


def test_created_user_can_login(client):
    create_response = client.post(
        "/api/v1/users/",
        json={
            "username": "login_user",
            "email": "login_user@meallist.local",
            "password": TEST_PASSWORD,
        },
    )

    assert create_response.status_code == 200

    token = login(client, "login_user@meallist.local")

    assert isinstance(token, str)
    assert len(token) > 0


def test_users_me_returns_authenticated_user(client, session):
    user = load_user(session, "chef_john")
    token = login(client, user.email)

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(user.id)
    assert body["username"] == user.username
    assert body["email"] == user.email
    assert "password" not in body
    assert "password_hash" not in body


def test_users_me_without_token_fails(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_users_me_with_invalid_token_fails(client):
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_disabled_user_cannot_access_users_me(client, session):
    user = load_user(session, "inactive_user")
    token = login(client, user.email)

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401
