from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Food Recognition API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/food_db"

    OPENFOODFACTS_API_URL: str = "https://world.openfoodfacts.org/api/v0/product"
    OPENFOODFACTS_SEARCH_URL: str = "https://world.openfoodfacts.org/cgi/search.pl"
    GOOGLE_PLACES_API_KEY: str = ""
    OPEN_PRICES_API_URL: str = "https://api.openfoodfacts.org/api/v1/price"

    MODEL_PATH: str = "../ml/model.pth"
    CONFIDENCE_THRESHOLD: float = 0.7

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
