from pathlib import Path

from app.models.user import User
from tests.loaders.base import load_json, load_many, load_single

DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"


def load_user(session, name: str) -> User:
    data = load_json(DATA_FILE)

    return load_single(
        session=session,
        model=User,
        data=data[name],
        builder=User.model_validate,
    )


def load_all_users(session) -> list[User]:
    return load_many(
        session=session,
        model=User,
        data=load_json(DATA_FILE),
        builder=User.model_validate,
    )
