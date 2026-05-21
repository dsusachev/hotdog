import httpx
from src.core.logger import logger

OPEN_PRICES_URL = "https://prices.openfoodfacts.org/api/v1"


class OpenPricesClient:
    def __init__(self):
        self.baseUrl = OPEN_PRICES_URL
        self.headers = {
            "User-Agent": "HotDogApp/0.1.0 (educational project)",
        }

    async def getPricesByBarcode(self, barcode: str, limit: int = 10) -> list:
        """Получить цены по штрихкоду продукта"""
        params = {
            "product_code": barcode,
            "page_size": limit,
        }
        return await self._get("/prices", params)

    async def getPricesByProductName(self, query: str, limit: int = 10) -> list:
        """Получить цены по названию продукта (через поиск штрихкода)"""
        params = {
            "product_name__icontains": query,
            "page_size": limit,
        }
        return await self._get("/prices", params)

    async def _get(self, path: str, params: dict) -> list:
        try:
            async with httpx.AsyncClient(
                timeout=3.0,
                headers=self.headers,
            ) as client:
                response = await client.get(
                    f"{self.baseUrl}{path}",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
        except httpx.TimeoutException:
            logger.warning("Open Prices API timeout")
            return []
        except Exception as e:
            logger.error(f"Open Prices API error: {e}")
            return []


openPricesClient = OpenPricesClient()
