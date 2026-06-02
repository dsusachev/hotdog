import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import getCurrentUserOptional
from src.core.logger import logger
from src.db.database import getDb
from src.db.models.search_history import SearchHistory
from src.db.models.user import User
from src.services.openFoodFactsClient import openFoodFactsClient

router = APIRouter(tags=["products"])


class NutritionFacts(BaseModel):
    calories_per_100g: float | None = None
    proteins_per_100g: float | None = None
    fats_per_100g: float | None = None
    carbs_per_100g: float | None = None
    sugar_per_100g: float | None = None
    fiber_per_100g: float | None = None
    salt_per_100g: float | None = None


class ProductSearchItem(BaseModel):
    id: str
    name: str
    brand: str | None = None
    categories: str | None = None
    image_url: str | None = None
    nutrition: NutritionFacts


class ProductSearchResponse(BaseModel):
    query: str
    total: int
    products: list[ProductSearchItem]


class ProductDetailResponse(BaseModel):
    id: str
    name: str
    brand: str | None = None
    categories: str | None = None
    image_url: str | None = None
    nutrition: NutritionFacts
    ingredients: str | None = None
    description: str | None = None


def buildDescription(raw: dict) -> str | None:
    parts = []
    if raw.get("brands"):
        parts.append(raw["brands"])
    if raw.get("categories"):
        first_category = raw["categories"].split(",")[0].strip()
        parts.append(first_category)
    return ", ".join(parts) if parts else None


def parseNutrition(nutriments: dict) -> NutritionFacts:
    return NutritionFacts(
        calories_per_100g=nutriments.get("energy-kcal_100g"),
        proteins_per_100g=nutriments.get("proteins_100g"),
        fats_per_100g=nutriments.get("fat_100g"),
        carbs_per_100g=nutriments.get("carbohydrates_100g"),
        sugar_per_100g=nutriments.get("sugars_100g"),
        fiber_per_100g=nutriments.get("fiber_100g"),
        salt_per_100g=nutriments.get("salt_100g"),
    )


def parseProduct(raw: dict) -> ProductSearchItem | None:
    name = raw.get("product_name", "").strip()
    if not name:
        return None
    return ProductSearchItem(
        id=raw.get("code", ""),
        name=name,
        brand=raw.get("brands") or None,
        categories=raw.get("categories") or None,
        image_url=raw.get("image_url") or None,
        nutrition=parseNutrition(raw.get("nutriments", {})),
    )


@router.get(
    "/products/search",
    response_model=ProductSearchResponse,
    summary="Поиск продуктов",
    description="Ищет продукты в базе Open Food Facts по названию. Возвращает название, бренд, категории, КБЖУ и ссылку на фото.",
)
async def searchProducts(
    query: str = Query(
        ..., min_length=1, max_length=100, description="Название продукта"
    ),
    db: AsyncSession = Depends(getDb),
    currentUser: User | None = Depends(getCurrentUserOptional),
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"Searching products: '{query}'")
    rawProducts = await openFoodFactsClient.searchProducts(query)

    products = [
        parsed for raw in rawProducts if (parsed := parseProduct(raw)) is not None
    ]

    if currentUser:
        try:
            history = SearchHistory(
                id=uuid.uuid4(),
                user_id=currentUser.id,
                query_text=query,
                raw_ml_response={
                    "type": "search",
                    "query": query,
                    "results_count": len(products),
                },
            )
            db.add(history)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.warning(f"Failed to save search history: {e}")

    logger.info(f"Found {len(products)} products for query '{query}'")
    return ProductSearchResponse(
        query=query,
        total=len(products),
        products=products,
    )


@router.get(
    "/products/{productId}",
    response_model=ProductDetailResponse,
    summary="Детали продукта по штрих-коду",
    description="Возвращает полную информацию о продукте: состав, КБЖУ, ингредиенты.",
)
async def getProduct(productId: str):
    logger.info(f"Getting product by id: '{productId}'")
    raw = await openFoodFactsClient.getProductById(productId)

    if not raw:
        raise HTTPException(status_code=404, detail="Product not found")

    name = raw.get("product_name", "").strip()
    if not name:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductDetailResponse(
        id=raw.get("code", productId),
        name=name,
        brand=raw.get("brands") or None,
        categories=raw.get("categories") or None,
        image_url=raw.get("image_url") or None,
        nutrition=parseNutrition(raw.get("nutriments", {})),
        ingredients=raw.get("ingredients_text") or None,
        description=buildDescription(raw),
    )
