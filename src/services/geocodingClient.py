import httpx
from src.core.logger import logger

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


class GeocodingClient:
    def __init__(self):
        self.headers = {"User-Agent": "HotDogApp/0.1.0 (educational project)"}

    async def reverseGeocode(self, lat: float, lng: float) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=8.0, headers=self.headers) as client:
                r = await client.get(NOMINATIM_URL, params={
                    "lat": lat,
                    "lon": lng,
                    "format": "json",
                    "accept-language": "ru",
                })
                r.raise_for_status()
                data = r.json()

                addr = data.get("address", {})
                return {
                    "display_name": data.get("display_name"),
                    "city": addr.get("city") or addr.get("town") or addr.get("village"),
                    "country": addr.get("country"),
                    "street": addr.get("road"),
                    "house": addr.get("house_number"),
                }
        except Exception as e:
            logger.warning(f"Geocoding failed for ({lat}, {lng}): {e}")
            return None


geocodingClient = GeocodingClient()
