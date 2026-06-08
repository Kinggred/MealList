from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.user import router as user_router

from app.core.settings import get_settings

app = FastAPI()
settings = get_settings()

api_router = APIRouter()

app.include_router(api_router)
app.include_router(auth_router)
app.include_router(user_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
