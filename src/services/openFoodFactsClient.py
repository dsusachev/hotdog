import httpx
from src.core.config import settings
from src.core.logger import logger


class OpenFoodFactsClient:
    def __init__(self):
        self.baseUrl = settings.OPEN_FOOD_FACTS_URL

    async def searchProducts(self, query: str, pageSize: int = 10) -> list:
        params = {
            "search_terms": query,
            "page_size": pageSize,
            "json": 1,
            "fields": "code,product_name,brands,categories,nutriments,image_url",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.baseUrl}/search",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("products", [])
        except httpx.TimeoutException:
            logger.warning("Open Food Facts API timeout")
            return []
        except Exception as e:
            logger.error(f"Open Food Facts API error: {e}")
            return []


openFoodFactsClient = OpenFoodFactsClient()
