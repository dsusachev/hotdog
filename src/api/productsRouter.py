from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List

from src.core.logger import logger
from src.services.openFoodFactsClient import openFoodFactsClient

router = APIRouter()


class NutritionFacts(BaseModel):
    calories_per_100g: float | None = None
    proteins_per_100g: float | None = None
    fats_per_100g: float | None = None
    carbs_per_100g: float | None = None


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
    products: List[ProductSearchItem]


def parseNutrition(nutriments: dict) -> NutritionFacts:
    return NutritionFacts(
        calories_per_100g=nutriments.get("energy-kcal_100g"),
        proteins_per_100g=nutriments.get("proteins_100g"),
        fats_per_100g=nutriments.get("fat_100g"),
        carbs_per_100g=nutriments.get("carbohydrates_100g"),
    )


def parseProduct(raw: dict) -> ProductSearchItem | None:
    name = raw.get("product_name", "").strip()
    if not name:
        return None

    return ProductSearchItem(
        id=raw.get("code", ""),
        name=name,
        brand=raw.get("brands", None),
        categories=raw.get("categories", None),
        image_url=raw.get("image_url", None),
        nutrition=parseNutrition(raw.get("nutriments", {})),
    )


@router.get("/products/search", response_model=ProductSearchResponse)
async def searchProducts(
    query: str = Query(..., min_length=1, max_length=100, description="Название продукта"),
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"Searching products: '{query}'")

    rawProducts = await openFoodFactsClient.searchProducts(query)

    products = [
        parsed
        for raw in rawProducts
        if (parsed := parseProduct(raw)) is not None
    ]

    logger.info(f"Found {len(products)} products for query '{query}'")

    return ProductSearchResponse(
        query=query,
        total=len(products),
        products=products,
    )
