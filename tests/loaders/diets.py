import json
from pathlib import Path
from uuid import UUID

from app.models.diet import Diet

DATA_FILE = Path(__file__).parent.parent / "data" / "diets.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_diet(session, name: str) -> Diet:
    data = _load_data()[name]

    diet = Diet(
        id=UUID(data["id"]),
        name=data["name"],
        content=data["content"],
        created_by=UUID(data["created_by"]),
    )

    session.add(diet)
    session.commit()
    session.refresh(diet)

    return diet


def load_all_diets(session) -> list[Diet]:
    diets = []

    for data in _load_data().values():
        diet = Diet(
            id=UUID(data["id"]),
            name=data["name"],
            content=data["content"],
            created_by=UUID(data["created_by"]),
        )
        diets.append(diet)

    session.add_all(diets)
    session.commit()

    for diet in diets:
        session.refresh(diet)

    return diets
