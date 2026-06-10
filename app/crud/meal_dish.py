from app.crud.base import CRUDBase
from app.models.meal_dish import MealDish, MealDishCreate, MealDishUpdate


class CRUDMealDish(CRUDBase[MealDish, MealDishCreate, MealDishUpdate]):
    pass


meal_dish_crud = CRUDMealDish(MealDish)
