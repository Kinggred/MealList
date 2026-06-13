from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.diet import diet_router
from app.api.endpoints.ingredient import ingredient_router
from app.api.endpoints.meal import meal_router
from app.api.endpoints.recipe import recipe_router
from app.api.endpoints.user import router as user_router

from app.core.settings import get_settings

app = FastAPI()
add_pagination(app)
settings = get_settings()


api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health")
def health():
    return {"status": "ok"}


api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["user"])
api_router.include_router(
    ingredient_router, prefix="/ingredients", tags=["ingredients"]
)

api_router.include_router(recipe_router, prefix="/recipes", tags=["recipe"])
api_router.include_router(diet_router, prefix="/diets", tags=["diet"])

api_router.include_router(meal_router, prefix="/meals", tags=["meal"])

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
