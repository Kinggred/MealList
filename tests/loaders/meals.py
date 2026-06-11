import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from app.models.meal import Meal

DATA_FILE = Path(__file__).parent.parent / "data" / "meals.json"


def _load_data() -> dict:
    with open(DATA_FILE) as file:
        return json.load(file)


def load_meal(session, name: str) -> Meal:
    data = _load_data()[name]

    meal = Meal(
        id=UUID(data["id"]),
        name=data["name"],
        date=datetime.fromisoformat(data["date"]),
        created_by=UUID(data["created_by"]),
    )

    session.add(meal)
    session.commit()
    session.refresh(meal)

    return meal


def load_all_meals(session) -> list[Meal]:
    meals = []

    for data in _load_data().values():
        meal = Meal(
            id=UUID(data["id"]),
            name=data["name"],
            date=datetime.fromisoformat(data["date"]),
            created_by=UUID(data["created_by"]),
        )
        meals.append(meal)

    session.add_all(meals)
    session.commit()

    for meal in meals:
        session.refresh(meal)

    return meals
