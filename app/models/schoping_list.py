import math
from collections import defaultdict
from datetime import date
from typing import List

from sqlmodel import SQLModel
from uuid import UUID

from app.models.ingridient import Ingredient, Units
from app.models.meal_dish import MealDish
from app.models.recipe_ingredient import RecipeIngredient


class ShoppingListView(SQLModel):
    date_from: date
    date_to: date
    ingredient_list: list["IngredientInShoppingListView"]

    @classmethod
    def from_calculations(
        cls,
        *,
        date_from: date,
        date_to: date,
        calculations: list["IngredientsCalculationsView"],
        ingredients: list["Ingredient"],
    ) -> "ShoppingListView":
        ingredient_by_id = {
            ingredient.id: ingredient
            for ingredient in ingredients
        }

        return cls(
            date_from=date_from,
            date_to=date_to,
            ingredient_list=[
                IngredientInShoppingListView.from_calculation(
                    calculation=calculation,
                    ingredient=ingredient_by_id[calculation.ingredient_id],
                )
                for calculation in calculations
                if calculation.ingredient_id in ingredient_by_id
            ],
        )

class IngredientInShoppingListView(SQLModel):
    id: UUID
    name: str
    exact_amount: float
    amount: float
    estimated_cost: float
    unit_of_measurement: Units

    @classmethod
    def from_calculation(
        cls,
        calculation: "IngredientsCalculationsView",
        ingredient: "Ingredient",
    ) -> "IngredientInShoppingListView":
        exact_amount = calculation.amount

        rounded_amount = math.ceil(
            exact_amount / ingredient.amount_per_cost
        ) * ingredient.amount_per_cost

        return cls(
            id=ingredient.id,
            name=ingredient.name,
            exact_amount=round(exact_amount, 2),
            amount=round(rounded_amount, 2),
            estimated_cost=round(calculation.estimated_cost, 2),
            unit_of_measurement = ingredient.unit_of_measurement
        )

class DishesCalculationsView(SQLModel):
    recipe_id: UUID
    full_portions: int
    half_portions: int

    @classmethod
    def from_meal_dishes(
            cls,
            meal_dishes: list[MealDish],
    ) -> list["DishesCalculationsView"]:
        aggregated = defaultdict(
            lambda: {
                "full_portions": 0,
                "half_portions": 0,
            }
        )

        for meal_dish in meal_dishes:
            effective_full_portions = (
                    meal_dish.full_portions + math.ceil(meal_dish.half_portions / 2)
            )

            aggregated[meal_dish.recipe_id]["full_portions"] += effective_full_portions
            aggregated[meal_dish.recipe_id]["half_portions"] += 0

        return [
            cls(
                recipe_id=recipe_id,
                full_portions=data["full_portions"],
                half_portions=data["half_portions"],
            )
            for recipe_id, data in aggregated.items()
        ]

class IngredientsCalculationsView(SQLModel):
    ingredient_id: UUID
    amount: float
    estimated_cost: float

    @classmethod
    def from_recipe_ingredients(
        cls,
        dishes: list["DishesCalculationsView"],
        rows: list[tuple[RecipeIngredient, Ingredient]],
    ) -> list["IngredientsCalculationsView"]:
        recipe_portions = {
            dish.recipe_id: dish.full_portions + math.ceil(dish.half_portions / 2)
            for dish in dishes
        }

        aggregated = defaultdict(
            lambda: {
                "amount": 0.0,
                "estimated_cost": 0.0,
            }
        )

        for recipe_ingredient, ingredient in rows:
            portions = recipe_portions.get(recipe_ingredient.recipe_id, 0)

            required_amount = recipe_ingredient.amount * portions

            estimated_cost = (
                ingredient.cost
                * required_amount
                / ingredient.amount_per_cost
            )

            aggregated[ingredient.id]["amount"] += required_amount
            aggregated[ingredient.id]["estimated_cost"] += estimated_cost

        return [
            cls(
                ingredient_id=ingredient_id,
                amount=data["amount"],
                estimated_cost=round(data["estimated_cost"], 2),
            )
            for ingredient_id, data in aggregated.items()
        ]