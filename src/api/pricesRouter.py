from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List

from src.core.logger import logger
from src.services.yandexPlacesClient import yandexPlacesClient

router = APIRouter()


class PlaceItem(BaseModel):
    name: str
    address: str
    category: str
    latitude: float | None = None
    longitude: float | None = None
    url: str | None = None


class PricesResponse(BaseModel):
    product: str
    latitude: float
    longitude: float
    total: int
    places: List[PlaceItem]


@router.get("/prices", response_model=PricesResponse)
async def getPrices(
    product: str = Query(..., min_length=1, max_length=100, description="Название продукта"),
    lat: float = Query(..., ge=-90, le=90, description="Широта"),
    lng: float = Query(..., ge=-180, le=180, description="Долгота"),
):
    logger.info(f"Searching places for '{product}' near ({lat}, {lng})")

    # Ищем магазины и кафе где можно купить продукт
    searchQuery = f"купить {product}"
    places = await yandexPlacesClient.searchNearby(searchQuery, lat, lng)

    if not places:
        logger.info(f"No places found for '{product}'")

    parsed = [
        PlaceItem(
            name=p["name"],
            address=p["address"],
            category=p["category"],
            latitude=p.get("latitude"),
            longitude=p.get("longitude"),
            url=p.get("url"),
        )
        for p in places
    ]

    return PricesResponse(
        product=product,
        latitude=lat,
        longitude=lng,
        total=len(parsed),
        places=parsed,
    )
