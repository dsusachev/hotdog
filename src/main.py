from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import settings
from src.core.errorHandlers import (
    httpExceptionHandler,
    validationExceptionHandler,
    unexpectedExceptionHandler,
)
from src.core.loggingMiddleware import loggingMiddleware
from src.api.router import router
from src.api.healthRouter import router as healthRouter
from src.api.classifyRouter import router as classifyRouter
from src.api.productsRouter import router as productsRouter
from src.api.pricesRouter import router as pricesRouter
from src.api.authRouter import router as authRouter
from src.api.feedbackRouter import router as feedbackRouter
from src.db.database import engine
from src.db.models.user import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for food recognition service",
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

app.include_router(router, prefix="/api")
app.include_router(healthRouter)
app.include_router(classifyRouter, prefix="/api")
app.include_router(productsRouter, prefix="/api")
app.include_router(pricesRouter, prefix="/api")
app.include_router(authRouter, prefix="/api")
app.include_router(feedbackRouter, prefix="/api")
