import httpx
from src.core.config import settings
from src.core.logger import logger

MAX_RETRIES = 2


class OpenFoodFactsClient:
    def __init__(self):
        self.baseUrl = settings.OPEN_FOOD_FACTS_URL
        self.headers = {
            "User-Agent": "HotDogApp/0.1.0 (educational project)",
        }

    async def searchProducts(self, query: str, pageSize: int = 10) -> list:
        params = {
            "search_terms": query,
            "page_size": pageSize,
            "json": 1,
            "fields": "code,product_name,brands,categories,nutriments,image_url",
        }
        return await self._getWithRetry("/search", params)

    async def getProductById(self, productId: str) -> dict | None:
        result = await self._getWithRetry(f"/product/{productId}")
        if result and result.get("status") == 1:
            return result.get("product")
        return None

    async def _getWithRetry(self, path: str, params: dict = None) -> list | dict:
        lastError = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=5.0,
                    headers=self.headers,
                ) as client:
                    response = await client.get(
                        f"{self.baseUrl}{path}",
                        params=params,
                    )
                    response.raise_for_status()
                    data = response.json()

                    # Для поиска возвращаем список, для продукта — словарь
                    if isinstance(data, dict) and "products" in data:
                        return data.get("products", [])
                    return data

            except httpx.TimeoutException as e:
                lastError = e
                logger.warning(
                    f"Open Food Facts timeout (attempt {attempt}/{MAX_RETRIES})"
                )
            except httpx.HTTPStatusError as e:
                lastError = e
                logger.error(
                    f"Open Food Facts HTTP error {e.response.status_code} "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                break  # При HTTP ошибке не повторяем
            except Exception as e:
                lastError = e
                logger.error(
                    f"Open Food Facts unexpected error: {e} "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )

        logger.error(f"Open Food Facts failed after {MAX_RETRIES} attempts: {lastError}")
        return []


openFoodFactsClient = OpenFoodFactsClient()
