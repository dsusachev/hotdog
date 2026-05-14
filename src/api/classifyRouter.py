from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.config import settings
from src.core.logger import logger
from src.services.mlServiceClient import mlServiceClient

router = APIRouter()


def validateImage(file: UploadFile) -> None:
    extension = file.filename.split(".")[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )


@router.post("/classify")
async def classifyImage(file: UploadFile = File(...)):
    validateImage(file)

    imageBytes = await file.read()

    maxBytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(imageBytes) > maxBytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB} MB",
        )

    logger.info(f"Classifying image: {file.filename} ({len(imageBytes)} bytes)")

    result = await mlServiceClient.classify(imageBytes, file.filename)

    if result.get("confidence", 0) < settings.CONFIDENCE_THRESHOLD:
        return {
            "status": "unrecognized",
            "message": "Could not recognize the product on the image",
            "confidence": result.get("confidence"),
        }

    return {
        "status": "ok",
        "category": result.get("category"),
        "confidence": result.get("confidence"),
        "mock": result.get("mock", False),
    }
