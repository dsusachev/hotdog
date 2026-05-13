from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.router import router

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


@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}
