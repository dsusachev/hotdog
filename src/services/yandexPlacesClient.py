import httpx

from src.core.logger import logger

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


class OverpassClient:
    def __init__(self):
        self.url = OVERPASS_URL
        self.headers = {
            "User-Agent": "HotDogApp/0.1.0 (educational project)",
        }

    async def searchNearby(
        self,
        query: str,
        lat: float,
        lng: float,
        radius: int = 2000,
        limit: int = 10,
    ) -> list:
        # Ищем магазины, кафе и рестораны поблизости
        overpassQuery = f"""
        [out:json][timeout:10];
        (
          node["shop"="supermarket"](around:{radius},{lat},{lng});
          node["shop"="convenience"](around:{radius},{lat},{lng});
          node["shop"="grocery"](around:{radius},{lat},{lng});
          node["amenity"="restaurant"](around:{radius},{lat},{lng});
          node["amenity"="fast_food"](around:{radius},{lat},{lng});
          node["amenity"="cafe"](around:{radius},{lat},{lng});
        );
        out body {limit};
        """

        try:
            async with httpx.AsyncClient(
                timeout=15.0,
                headers=self.headers,
            ) as client:
                response = await client.post(
                    self.url,
                    data={"data": overpassQuery},
                )
                response.raise_for_status()
                data = response.json()
                elements = data.get("elements", [])
                return [self._parsePlace(e) for e in elements if e.get("tags")]
        except httpx.TimeoutException:
            logger.warning("Overpass API timeout")
            return self._mockPlaces(lat, lng)
        except Exception as e:
            logger.error(f"Overpass API error: {e}")
            return self._mockPlaces(lat, lng)

    def _parsePlace(self, element: dict) -> dict:
        tags = element.get("tags", {})
        name = (
            tags.get("name")
            or tags.get("brand")
            or tags.get("operator")
            or "Unnamed place"
        )
        category = tags.get("shop") or tags.get("amenity") or "place"

        return {
            "name": name,
            "address": self._buildAddress(tags),
            "category": category,
            "latitude": element.get("lat"),
            "longitude": element.get("lon"),
            "url": tags.get("website") or None,
        }

    def _buildAddress(self, tags: dict) -> str:
        parts = []
        if tags.get("addr:street"):
            parts.append(tags["addr:street"])
        if tags.get("addr:housenumber"):
            parts.append(tags["addr:housenumber"])
        if tags.get("addr:city"):
            parts.append(tags["addr:city"])
        return ", ".join(parts) if parts else "Address unknown"

    def _mockPlaces(self, lat: float, lng: float) -> list:
        return [
            {
                "name": "Supermarket",
                "address": "Address unknown",
                "category": "supermarket",
                "latitude": lat + 0.001,
                "longitude": lng + 0.001,
                "url": None,
            }
        ]


yandexPlacesClient = OverpassClient()
