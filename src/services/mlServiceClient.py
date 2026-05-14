import httpx
from src.core.config import settings
from src.core.logger import logger


class MlServiceClient:
    def __init__(self):
        self.baseUrl = settings.ML_SERVICE_URL

    async def classify(self, imageBytes: bytes, fileName: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.baseUrl}/classify",
                    files={"file": (fileName, imageBytes, "image/jpeg")},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"ML Service unavailable, using mock: {e}")
            return self._mockResponse()

    def _mockResponse(self) -> dict:
        return {
            "category": "hotdog",
            "confidence": 0.91,
            "mock": True,
        }


mlServiceClient = MlServiceClient()
