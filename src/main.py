from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.authRouter import router as authRouter
from src.api.categoriesRouter import router as categoriesRouter
from src.api.classifyRouter import router as classifyRouter
from src.api.feedbackRouter import router as feedbackRouter
from src.api.healthRouter import router as healthRouter
from src.api.historyRouter import router as historyRouter
from src.api.modelRouter import router as modelRouter
from src.api.pricesRouter import router as pricesRouter
from src.api.productsRouter import router as productsRouter
from src.api.recipesRouter import router as recipesRouter
from src.api.router import router
from src.api.sprintRouter import router as sprintRouter
from src.core.config import settings
from src.core.errorHandlers import (
    httpExceptionHandler,
    unexpectedExceptionHandler,
    validationExceptionHandler,
)
from src.core.loggingMiddleware import loggingMiddleware
from src.db.database import engine
from src.db.models.user import Base

TAGS_METADATA = [
    {"name": "auth", "description": "Регистрация, вход, профиль пользователя"},
    {"name": "classify", "description": "Распознавание продукта по фотографии (ML)"},
    {"name": "products", "description": "Поиск продуктов через Open Food Facts"},
    {"name": "prices", "description": "Цены из Open Prices и ближайшие магазины/кафе"},
    {"name": "geocode", "description": "Обратное геокодирование координат в адрес"},
    {"name": "history", "description": "История запросов текущего пользователя"},
    {"name": "feedback", "description": "Отзывы пользователей"},
    {"name": "recipes", "description": "Рецепты из TheMealDB"},
    {"name": "categories", "description": "CRUD-справочник категорий продуктов"},
    {"name": "model", "description": "Информация о ML-модели (версия, список классов)"},
    {"name": "sprints", "description": "Управление спринтами и Burndown Chart"},
    {"name": "health", "description": "Проверка работоспособности сервиса"},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "REST API для сервиса распознавания продуктов питания.\n\n"
        "**Аутентификация:** Bearer JWT-токен в заголовке `Authorization`.\n\n"
        "**Базовый URL:** `/api`\n\n"
        "Документация доступна на `/docs` (Swagger UI) и `/redoc` (ReDoc)."
    ),
    contact={"name": "Hotdog Team"},
    openapi_tags=TAGS_METADATA,
)

app.add_exception_handler(HTTPException, httpExceptionHandler)
app.add_exception_handler(RequestValidationError, validationExceptionHandler)
app.add_exception_handler(Exception, unexpectedExceptionHandler)

app.add_middleware(BaseHTTPMiddleware, dispatch=loggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(router, prefix="/api")
app.include_router(healthRouter)
app.include_router(classifyRouter, prefix="/api")
app.include_router(productsRouter, prefix="/api")
app.include_router(pricesRouter, prefix="/api")
app.include_router(authRouter, prefix="/api")
app.include_router(feedbackRouter, prefix="/api")
app.include_router(historyRouter, prefix="/api")
app.include_router(recipesRouter, prefix="/api")
app.include_router(categoriesRouter, prefix="/api")
app.include_router(modelRouter, prefix="/api")
app.include_router(sprintRouter, prefix="/api")
