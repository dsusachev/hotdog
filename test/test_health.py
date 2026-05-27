import time
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем роутер из файла с health-эндпоинтом
from src.api.healthRouter import router
from src.db.database import getDb
from src.core.config import settings

settings.VERSION = "1.0.0-test"

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=None)

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[getDb] = override_get_db
    yield mock_session
    app.dependency_overrides.clear()


def test_health_ok(mock_db_session):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["version"] == "1.0.0-test"
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0
    assert data["services"]["database"] == "ok"

    mock_db_session.execute.assert_awaited_once()
    call_args = mock_db_session.execute.call_args[0][0]
    assert str(call_args) == "SELECT 1"


def test_health_db_unavailable(mock_db_session):
    mock_db_session.execute = AsyncMock(side_effect=Exception("Connection refused"))

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["services"]["database"] == "unavailable"
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0

    mock_db_session.execute.assert_awaited_once()
