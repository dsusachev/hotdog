import httpx
from src.core.config import settings
from src.core.logger import logger


class YandexPlacesClient:
    def __init__(self):
        self.placesUrl = settings.YANDEX_PLACES_URL

    async def searchNearby(
        self,
        query: str,
        lat: float,
        lng: float,
        limit: int = 10,
    ) -> list:
        if not settings.YANDEX_API_KEY:
            logger.warning("Yandex API key not set, returning mock places")
            return self._mockPlaces(query, lat, lng)

        params = {
            "apikey": settings.YANDEX_API_KEY,
            "text": query,
            "ll": f"{lng},{lat}",
            "spn": "0.1,0.1",  # Радиус поиска ~5 км
            "lang": "ru_RU",
            "results": limit,
            "type": "biz",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.placesUrl, params=params)
                response.raise_for_status()
                data = response.json()
                features = data.get("features", [])
                return [self._parsePlace(f) for f in features]
        except httpx.TimeoutException:
            logger.warning("Yandex Places API timeout")
            return []
        except Exception as e:
            logger.error(f"Yandex Places API error: {e}")
            return []

    def _parsePlace(self, feature: dict) -> dict:
        props = feature.get("properties", {})
        geo = feature.get("geometry", {})
        coords = geo.get("coordinates", [None, None])
        meta = props.get("CompanyMetaData", {})

        return {
            "name": props.get("name", ""),
            "address": meta.get("address", ""),
            "category": meta.get("Categories", [{}])[0].get("name", "") if meta.get("Categories") else "",
            "longitude": coords[0],
            "latitude": coords[1],
            "url": meta.get("url", None),
        }

    def _mockPlaces(self, query: str, lat: float, lng: float) -> list:
        return [
            {
                "name": f"Магазин 'Пятёрочка'",
                "address": "ул. Примерная, д. 1",
                "category": "Продуктовый магазин",
                "latitude": lat + 0.001,
                "longitude": lng + 0.001,
                "url": None,
            },
            {
                "name": f"Супермаркет 'Лента'",
                "address": "ул. Тестовая, д. 5",
                "category": "Супермаркет",
                "latitude": lat + 0.002,
                "longitude": lng - 0.001,
                "url": None,
            },
        ]


yandexPlacesClient = YandexPlacesClient()
