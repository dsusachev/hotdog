# test/test_main.py
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.db.database import getDb
from src.core.config import settings


@pytest.fixture
def client():
    """Фикстура тестового клиента."""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Подмена зависимости getDb мок-сессией для health-эндпоинта."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[getDb] = override_get_db
    yield mock_session
    app.dependency_overrides.clear()


def test_app_configuration():
    """Проверяет, что приложение создано с правильными метаданными."""
    assert app.title == settings.PROJECT_NAME
    assert app.version is not None and app.version != ""


def test_ping_endpoint(client):
    """Эндпоинт /api/ping должен вернуть pong."""
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_health_endpoint_ok(client, mock_db_session):
    """Health-эндпоинт при доступной БД возвращает статус ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == settings.VERSION
    assert "uptime_seconds" in data
    assert data["services"]["database"] == "ok"

    # Убеждаемся, что был выполнен SELECT 1
    mock_db_session.execute.assert_awaited_once()
    call_args = mock_db_session.execute.call_args[0][0]
    assert str(call_args) == "SELECT 1"


def test_health_endpoint_db_unavailable(client, mock_db_session):
    """При недоступной БД статус degraded, сервис БД unavailable."""
    mock_db_session.execute = AsyncMock(side_effect=Exception("Connection refused"))

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["services"]["database"] == "unavailable"
    mock_db_session.execute.assert_awaited_once()


def test_cors_headers(client):
    """Для разрешённого origin возвращается заголовок Access-Control-Allow-Origin."""
    allowed_origin = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost"
    response = client.get("/api/ping", headers={"Origin": allowed_origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == allowed_origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_blocks_disallowed_origin(client):
    """Для запрещённого origin заголовок Access-Control-Allow-Origin не возвращается."""
    response = client.get("/api/ping", headers={"Origin": "https://evil.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_router_prefixes():
    """Проверяет, что роутеры подключены с правильными префиксами."""
    routes = {route.path for route in app.routes}
    # Роутер из router.py подключён с префиксом /api
    assert "/api/ping" in routes
    # healthRouter подключён без префикса
    assert "/health" in routes
