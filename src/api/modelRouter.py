from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from src.core.logger import logger
from src.services.mlServiceClient import mlServiceClient

router = APIRouter(tags=["model"])


class ModelClassesResponse(BaseModel):
    model_version: str
    count: int
    classes: List[str]


@router.get("/model/classes", response_model=ModelClassesResponse, summary="Классы ML-модели", description="Возвращает список всех 43 категорий продуктов, которые умеет распознавать текущая ML-модель, и её версию.")
async def getModelClasses():
    logger.info("Model classes requested")
    result = await mlServiceClient.getClasses()
    if not result:
        raise HTTPException(status_code=503, detail="ML-сервис недоступен")
    return ModelClassesResponse(
        model_version=result["model_version"],
        count=result["count"],
        classes=result["classes"],
    )
