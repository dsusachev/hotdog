from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.core.logger import logger


def buildErrorResponse(status: int, message: str, details: list = None) -> dict:
    response = {
        "status": "error",
        "code": status,
        "message": message,
    }
    if details:
        response["details"] = details
    return response


async def httpExceptionHandler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(f"HTTP {exc.status_code} at {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=buildErrorResponse(exc.status_code, exc.detail),
    )


async def validationExceptionHandler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append({
            "field": field,
            "message": error["msg"],
        })

    logger.warning(f"Validation error at {request.url.path}: {details}")
    return JSONResponse(
        status_code=422,
        content=buildErrorResponse(
            422,
            "Ошибка валидации запроса",
            details,
        ),
    )


async def unexpectedExceptionHandler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=buildErrorResponse(500, "Внутренняя ошибка сервера"),
    )
