from fastapi import APIRouter, UploadFile, File
from src.core.config import settings
from src.core.logger import logger
from src.core.validation import validateImageFile
from src.services.mlServiceClient import mlServiceClient
from src.api.schemas import ClassifyResponse, TopPrediction, ErrorResponse

router = APIRouter()


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={400: {"model": ErrorResponse}},
)
async def classifyImage(file: UploadFile = File(...)):
    imageBytes = await file.read()

    validateImageFile(file, imageBytes)

    logger.info(f"Classifying image: {file.filename} ({len(imageBytes)} bytes)")

    result = await mlServiceClient.classify(imageBytes, file.filename)

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
