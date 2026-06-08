from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.ingredient import ingredient_router
from app.api.endpoints.user import router as user_router

from app.core.settings import get_settings

app = FastAPI()
add_pagination(app)
settings = get_settings()


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(
    ingredient_router, prefix="/ingredients", tags=["ingredients"]
)

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
