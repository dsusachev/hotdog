from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.router import router
from src.api.healthRouter import router as healthRouter
from src.api.classifyRouter import router as classifyRouter
from src.api.productsRouter import router as productsRouter

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for food recognition service",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(healthRouter)
app.include_router(classifyRouter, prefix="/api")
app.include_router(productsRouter, prefix="/api")
