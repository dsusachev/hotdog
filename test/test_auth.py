import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = Mock()
    user.id = UUID
    user.email = "test@example.com"
    user.password_hash = "hashed_password"
    user.display_name = "Test User"
    user.is_active = True
    return user


@pytest.fixture
def mock_db_session_with_user(mock_db_session, mock_user):
    """Mock database session with existing user"""
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=mock_user)
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    mock_db_session.add = Mock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    
    return mock_db_session


@pytest.fixture
def mock_db_session_no_user(mock_db_session):
    """Mock database session with no user"""
    mock_result = Mock()
    mock_result.scalar_one_or_none = Mock(return_value=None)
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    mock_db_session.add = Mock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'id', 1))
    
    return mock_db_session


# Override dependencies for testing
@pytest.fixture(autouse=True)
def override_dependencies(mock_db_session_no_user):
    """Override database dependency"""
    from src.db.database import getDb
    
    async def get_mock_db():
        return mock_db_session_no_user
    
    app.dependency_overrides[getDb] = get_mock_db
    yield
    app.dependency_overrides.clear()


def test_register_success(mock_db_session_no_user):
    """Регистрация нового пользователя — статус 200"""
    with patch("src.api.authRouter.hashPasswordAsync", new_callable=AsyncMock, return_value="hashed_pass"):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "secret123",
                "display_name": "New User",
            },
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "new@example.com"
    assert data["display_name"] == "New User"
    assert data["is_active"] == True


def test_register_duplicate_email(mock_db_session_with_user):
    """Попытка регистрации с существующим email — 400"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "existing@example.com",
            "password": "secret123",
            "display_name": "Existing User",
        },
    )
    
    assert response.status_code == 400
    response_data = response.json()
    # Ваш errorHandler может возвращать {"detail": "message"} или {"error": "message"}
    # Проверяем оба варианта
    if "detail" in response_data:
        assert "Email already registered" in response_data["detail"]
    elif "error" in response_data:
        assert "Email already registered" in response_data["error"]
    else:
        # Если ни того, ни другого, проверяем что сообщение есть в любом поле
        assert any("Email already registered" in str(v) for v in response_data.values())


def test_login_success(mock_db_session_with_user, mock_user):
    """Успешный логин — возвращается токен, статус 200"""
    with patch("src.api.authRouter.verifyPasswordAsync", new_callable=AsyncMock, return_value=True), \
         patch("src.api.authRouter.createAccessToken", return_value="fake_jwt_token"):
        response = client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "correct"},
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] == "fake_jwt_token"


def test_login_invalid_credentials(mock_db_session_no_user):
    """Неверный email или пароль — 401"""
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "anything"},
    )
    
    assert response.status_code == 401
    response_data = response.json()
    if "detail" in response_data:
        assert "Invalid credentials" in response_data["detail"]
    elif "error" in response_data:
        assert "Invalid credentials" in response_data["error"]
    else:
        assert any("Invalid credentials" in str(v) for v in response_data.values())


def test_login_wrong_password(mock_db_session_with_user, mock_user):
    """Email существует, но пароль неверен — 401"""
    with patch("src.api.authRouter.verifyPasswordAsync", new_callable=AsyncMock, return_value=False):
        response = client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "wrong"},
        )
    
    assert response.status_code == 401
    response_data = response.json()
    if "detail" in response_data:
        assert "Invalid credentials" in response_data["detail"]
    elif "error" in response_data:
        assert "Invalid credentials" in response_data["error"]
    else:
        assert any("Invalid credentials" in str(v) for v in response_data.values())


def test_login_inactive_user(mock_db_session_with_user, mock_user):
    """Попытка логина заблокированного пользователя — 403"""
    mock_user.is_active = False
    
    with patch("src.api.authRouter.verifyPasswordAsync", new_callable=AsyncMock, return_value=True):
        response = client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "correct"},
        )
    
    assert response.status_code == 403
    response_data = response.json()
    if "detail" in response_data:
        assert "Account disabled" in response_data["detail"]
    elif "error" in response_data:
        assert "Account disabled" in response_data["error"]
    else:
        assert any("Account disabled" in str(v) for v in response_data.values())


def test_login_missing_fields():
    """Отсутствие обязательных полей — 422"""
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com"}  # missing password
    )
    assert response.status_code == 422
    
    response = client.post(
        "/api/auth/login",
        json={"password": "secret123"}  # missing email
    )
    assert response.status_code == 422


def test_register_missing_fields():
    """Отсутствие обязательных полей при регистрации — 422"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com"}  # missing password and display_name
    )
    assert response.status_code == 422
