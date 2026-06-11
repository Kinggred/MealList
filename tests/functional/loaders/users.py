import json
from pathlib import Path

from app.models.user import User

DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"


def _load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def load_user(session, name: str) -> User:
    data = _load_data()[name]

    user = User.model_validate(data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def load_all_users(session) -> list[User]:
    data = _load_data()

    users = [User.model_validate(user_data) for user_data in data.values()]

    session.add_all(users)
    session.commit()

    for user in users:
        session.refresh(user)

    return users
