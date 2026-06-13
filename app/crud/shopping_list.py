from datetime import date, datetime, time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session
from weasyprint import HTML

from app.crud.ingredient import ingredient_crud
from app.crud.meal import meal_crud
from app.crud.meal_dish import meal_dish_crud
from app.crud.recipe_ingredient import recipe_ingredient_crud
from app.models.schoping_list import ShoppingListView
from app.models.user import User


class ShoppingList:
    TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "api" / "templates"

    @staticmethod
    def get_list_from_range(
        db: Session, user: User, date_from: date, date_to: date
    ) -> ShoppingListView:
        start_dt = datetime.combine(date_from, time.min)
        end_dt = datetime.combine(date_to, time.max)
        meal_ids = [
            meal.id
            for meal in meal_crud.get_meals_in_range(
                db=db, user=user, start_date=start_dt, end_date=end_dt
            ).results
        ]
        dishes = meal_dish_crud.get_dishes_from_meal_list(db=db, meal_ids=meal_ids)
        calculations = recipe_ingredient_crud.get_ingredient_calculations_from_dishes(
            db,
            dishes=dishes,
        )
        shopping_list = ingredient_crud.build_shopping_list(
            db,
            date_from=date_from,
            date_to=date_to,
            calculations=calculations,
        )
        return shopping_list

    def get_file_from_range(
        self, db: Session, user: User, date_from: date, date_to: date
    ) -> bytes:
        data = self.get_list_from_range(db, user, date_from, date_to)

        templates = Environment(
            loader=FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

        template = templates.get_template("shopping_list.html")

        total_cost = sum(
            ingredient.estimated_cost for ingredient in data.ingredient_list
        )
        html = template.render(data=data, total_cost=total_cost)

        return HTML(string=html, base_url=".").write_pdf()


shopping_list_crud = ShoppingList()
