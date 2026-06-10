from app.crud.base import CRUDBase
from app.models.diet_ingredient import DietIngredient, DietIngredientCreate


class CRUDDietIngredient(
    CRUDBase[DietIngredient, DietIngredientCreate, DietIngredientCreate]
):
    pass


diet_ingredient_crud = CRUDDietIngredient(DietIngredient)
