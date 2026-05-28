import uuid
from fastapi import APIRouter, Depends, UploadFile, File
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

router = APIRouter()


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={400: {"model": ErrorResponse}},
)
async def classifyImage(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    imageBytes = await file.read()

    validateImageFile(file, imageBytes)

    logger.info(f"Classifying image: {file.filename} ({len(imageBytes)} bytes)")

    result = await mlServiceClient.classify(imageBytes, file.filename)

    history = SearchHistory(
        id=uuid.uuid4(),
        query_text=file.filename,
        raw_ml_response=result,
    )
    db.add(history)
    await db.commit()

    isUnknown = result.get("confidence", 0) < settings.CONFIDENCE_THRESHOLD

    topK = [
        TopPrediction(
            category=p["category"],
            confidence=round(p["confidence"], 4),
        )
        for p in result.get("top_k", [])
    ]

    if isUnknown:
        logger.info(f"Image not recognized, confidence: {result.get('confidence')}")
        return ClassifyResponse(
            status="unknown",
            is_unknown=True,
            category=None,
            confidence=result.get("confidence"),
            top_k=topK,
            mock=result.get("mock", False),
        )

    logger.info(f"Classified as '{result.get('category')}' with confidence {result.get('confidence')}")
    return ClassifyResponse(
        status="ok",
        is_unknown=False,
        category=result.get("category"),
        confidence=round(result.get("confidence", 0), 4),
        top_k=topK,
        mock=result.get("mock", False),
    )
