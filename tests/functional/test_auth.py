from datetime import timedelta

import jwt
import pytest

from app.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.api.exceptions import UnauthorizedException
from app.core.settings import get_settings
from tests.loaders.users import load_user


def test_get_password_hash_creates_verifiable_hash():
    password = "password"

    password_hash = get_password_hash(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = get_password_hash("password")

    assert verify_password("wrong-password", password_hash) is False


def test_authenticate_user_returns_user_for_valid_credentials(session):
    user = load_user(session, "chef_john")
    user.password_hash = get_password_hash("test")
    session.add(user)
    session.commit()
    session.refresh(user)

    result = authenticate_user(
        db=session,
        email=user.email,
        password="test",
    )

    assert result is not None
    assert result.id == user.id
    assert result.email == user.email


def test_authenticate_user_returns_none_for_wrong_password(session):
    user = load_user(session, "chef_john")
    user.password_hash = get_password_hash("test")
    session.add(user)
    session.commit()

    result = authenticate_user(
        db=session,
        email=user.email,
        password="wrong-password",
    )

    assert result is None


def test_authenticate_user_returns_none_for_unknown_email(session):
    result = authenticate_user(
        db=session,
        email="missing@meallist.local",
        password="password",
    )

    assert result is None


def test_create_access_token_encodes_subject():
    settings = get_settings()

    token = create_access_token(
        data={"sub": "john@meallist.local"},
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == "john@meallist.local"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_get_current_user_returns_user_for_valid_token(session):
    user = load_user(session, "chef_john")

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=5),
    )

    result = await get_current_user(
        db=session,
        token=token,
    )

    assert result.id == user.id
    assert result.email == user.email


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(session):
    with pytest.raises(UnauthorizedException):
        await get_current_user(
            db=session,
            token="invalid-token",
        )


@pytest.mark.asyncio
async def test_get_current_user_rejects_token_without_sub(session):
    token = create_access_token(
        data={"not_sub": "john@meallist.local"},
        expires_delta=timedelta(minutes=5),
    )

    with pytest.raises(UnauthorizedException):
        await get_current_user(
            db=session,
            token=token,
        )


@pytest.mark.asyncio
async def test_get_current_user_rejects_unknown_user(session):
    token = create_access_token(
        data={"sub": "missing@meallist.local"},
        expires_delta=timedelta(minutes=5),
    )

    with pytest.raises(UnauthorizedException):
        await get_current_user(
            db=session,
            token=token,
        )


@pytest.mark.asyncio
async def test_get_current_active_user_returns_enabled_user(session):
    user = load_user(session, "chef_john")

    result = await get_current_active_user(current_user=user)

    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_current_active_user_rejects_disabled_user(session):
    user = load_user(session, "inactive_user")

    with pytest.raises(UnauthorizedException):
        await get_current_active_user(current_user=user)
