import json
from pathlib import Path
from typing import Callable, TypeVar
from uuid import UUID

from sqlmodel import Session

T = TypeVar("T")


def load_json(path: Path) -> dict:
    with open(path) as file:
        return json.load(file)


def load_single(
    session: Session,
    model: type[T],
    data: dict,
    builder: Callable[[dict], T],
) -> T:
    object_id = UUID(data["id"])

    existing = session.get(model, object_id)
    if existing:
        return existing

    obj = builder(data)

    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj


def load_many(
    session: Session,
    model: type[T],
    data: dict,
    builder: Callable[[dict], T],
) -> list[T]:
    objects = []

    for item in data.values():
        object_id = UUID(item["id"])

        existing = session.get(model, object_id)

        if existing:
            objects.append(existing)
            continue

        obj = builder(item)

        session.add(obj)
        objects.append(obj)

    session.commit()

    for obj in objects:
        session.refresh(obj)

    return objects
