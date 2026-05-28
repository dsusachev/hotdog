import httpx
from src.core.logger import logger

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

CATEGORY_MAP = {
    "breakfast": "Breakfast",
    "lunch":     "Chicken",
    "dinner":    "Seafood",
    "snack":     "Dessert",
}


class MealDbClient:
    async def _get(self, path: str, params: dict = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                r = await client.get(f"{BASE_URL}{path}", params=params)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.warning(f"MealDB error: {e}")
            return {}

    async def getByCategory(self, category: str) -> list:
        data = await self._get("/filter.php", {"c": category})
        return data.get("meals") or []

    async def getById(self, meal_id: str) -> dict | None:
        data = await self._get("/lookup.php", {"i": meal_id})
        meals = data.get("meals")
        return meals[0] if meals else None

    async def search(self, query: str) -> list:
        data = await self._get("/search.php", {"s": query})
        return data.get("meals") or []


mealDbClient = MealDbClient()
