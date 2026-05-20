from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List

from src.core.logger import logger
from src.services.yandexPlacesClient import yandexPlacesClient
from src.services.openPricesClient import openPricesClient

router = APIRouter()


class PriceItem(BaseModel):
    store_name: str
    price: float
    currency: str = "EUR"
    address: str | None = None
    source: str = "open_prices"


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
    prices: List[PriceItem]
    places: List[PlaceItem]
    prices_available: bool  # True если нашли данные в Open Prices


def parsePrice(raw: dict) -> PriceItem | None:
    price = raw.get("price")
    if price is None:
        return None

    location = raw.get("location", {}) or {}
    storeName = (
        location.get("name")
        or location.get("osm_name")
        or "Неизвестный магазин"
    )
    address = location.get("address") or None

    return PriceItem(
        store_name=storeName,
        price=float(price),
        currency=raw.get("currency", "EUR"),
        address=address,
        source="open_prices",
    )


@router.get("/prices", response_model=PricesResponse)
async def getPrices(
    product: str = Query(..., min_length=1, max_length=100, description="Название продукта"),
    lat: float = Query(..., ge=-90, le=90, description="Широта"),
    lng: float = Query(..., ge=-180, le=180, description="Долгота"),
):
    logger.info(f"Getting prices for '{product}' near ({lat}, {lng})")

    # Шаг 1 — пробуем Open Prices
    rawPrices = await openPricesClient.getPricesByProductName(product)
    prices = [
        parsed
        for raw in rawPrices
        if (parsed := parsePrice(raw)) is not None
    ]
    pricesAvailable = len(prices) > 0

    if pricesAvailable:
        logger.info(f"Found {len(prices)} prices in Open Prices for '{product}'")
    else:
        logger.info(f"No prices in Open Prices for '{product}', falling back to Yandex Places")

    # Шаг 2 — всегда ищем места поблизости через Yandex
    searchQuery = f"купить {product}"
    rawPlaces = await yandexPlacesClient.searchNearby(searchQuery, lat, lng)
    places = [
        PlaceItem(
            name=p["name"],
            address=p["address"],
            category=p["category"],
            latitude=p.get("latitude"),
            longitude=p.get("longitude"),
            url=p.get("url"),
        )
        for p in rawPlaces
    ]

    return PricesResponse(
        product=product,
        latitude=lat,
        longitude=lng,
        prices=prices,
        places=places,
        prices_available=pricesAvailable,
    )
