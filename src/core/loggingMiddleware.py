import time
from fastapi import Request
from src.core.logger import logger


async def loggingMiddleware(request: Request, callNext):
    startTime = time.time()

    # Логируем входящий запрос
    logger.info(
        f"→ {request.method} {request.url.path}"
        + (f"?{request.url.query}" if request.url.query else "")
    )

    try:
        response = await callNext(request)
    except Exception as exc:
        duration = round((time.time() - startTime) * 1000)
        logger.error(f"✗ {request.method} {request.url.path} — FAILED ({duration}ms): {exc}")
        raise

    duration = round((time.time() - startTime) * 1000)
    logger.info(
        f"← {request.method} {request.url.path} "
        f"— {response.status_code} ({duration}ms)"
    )

    return response
