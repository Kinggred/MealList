from app.crud.base import CRUDBase
from app.models.ingridient import Ingredient, IngredientCreate, IngredientUpdate


class CRUDIngredient(CRUDBase[Ingredient, IngredientCreate, IngredientUpdate]):
    pass


crud_ingredient = CRUDIngredient(Ingredient)
