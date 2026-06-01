import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.core.logger import logger
from src.core.validation import validateImageFile
from src.db.database import getDb
from src.db.models.search_history import SearchHistory
from src.db.models.user import User
from src.services.mlServiceClient import mlServiceClient
from src.api.schemas import ClassifyResponse, TopPrediction, ErrorResponse
from src.core.dependencies import getCurrentUser

router = APIRouter(tags=["classify"])


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Распознать продукт на фото",
    description=(
        "Принимает изображение (JPEG/PNG, до 5 МБ) и возвращает результат классификации ML-моделью.\n\n"
        "- `status: ok` — продукт распознан с уверенностью выше порога\n"
        "- `status: unknown` — модель не уверена (confidence < threshold)\n\n"
        "Опционально принимает координаты (`lat`, `lng`) — сохраняются вместе с историей."
    ),
)
async def classifyImage(
    file: UploadFile = File(...),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    imageBytes = await file.read()

    validateImageFile(file, imageBytes)

    logger.info(f"Classifying image: {file.filename} ({len(imageBytes)} bytes)")

    result = await mlServiceClient.classify(imageBytes, file.filename)

    location = {"lat": lat, "lng": lng} if lat is not None and lng is not None else {}
    history = SearchHistory(
        id=uuid.uuid4(),
        user_id=currentUser.id,
        query_text=file.filename,
        raw_ml_response={**result, "type": "classify", **location},
    )
    db.add(history)
    await db.commit()

    confidence = result.get("confidence") or 0
    isUnknown = confidence < settings.CONFIDENCE_THRESHOLD

    topK = [
        TopPrediction(
            category=p["category"],
            confidence=round(p["confidence"], 4),
        )
        for p in result.get("top_k", [])
    ]

    if isUnknown:
        logger.info(f"Image not recognized, confidence: {confidence}")
        return ClassifyResponse(
            status="unknown",
            is_unknown=True,
            category=None,
            confidence=confidence,
            top_k=topK,
            mock=result.get("mock", False),
        )

    logger.info(f"Classified as '{result.get('category')}' with confidence {confidence}")
    return ClassifyResponse(
        status="ok",
        is_unknown=False,
        category=result.get("category"),
        confidence=round(confidence, 4),
        top_k=topK,
        mock=result.get("mock", False),
    )
