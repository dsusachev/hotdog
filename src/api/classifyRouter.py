from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.config import settings
from src.core.logger import logger
from src.services.mlServiceClient import mlServiceClient
from src.api.schemas import ClassifyResponse, TopPrediction, ErrorResponse

router = APIRouter()


def validateImage(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    extension = file.filename.split(".")[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={400: {"model": ErrorResponse}},
)
async def classifyImage(file: UploadFile = File(...)):
    validateImage(file)

    imageBytes = await file.read()

    if len(imageBytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    maxBytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(imageBytes) > maxBytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB} MB",
        )

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
