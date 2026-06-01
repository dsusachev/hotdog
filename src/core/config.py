from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "HotDog API"
    VERSION: str = "0.1.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "hotdog"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    CONFIDENCE_THRESHOLD: float = 0.5

    # External APIs
    OPEN_FOOD_FACTS_URL: str = "https://world.openfoodfacts.org/api/v2"
    YANDEX_API_KEY: str = ""
    YANDEX_GEOCODER_URL: str = "https://geocode-maps.yandex.ru/1.x"
    YANDEX_PLACES_URL: str = "https://search-maps.yandex.ru/v1"

    # File upload
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]

    # Admin
    ADMIN_EMAIL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
