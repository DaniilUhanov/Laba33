from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

# Тестовые данные
TEST_USER = {
    "username": "test_user_123",
    "email": "test_user_123@example.com",
    "full_name": "Test User",
    "password": "strongpassword123"
}

# Глобальная переменная для хранения токена
access_token = None

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    """Фикстура для очистки тестовых данных после всех тестов"""
    yield
    # Удаление тестового пользователя если он был создан
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        client.delete("/users/me", headers=headers)

def test_create_user():
    """Тест создания нового пользователя"""
    response = client.post("/register/", json=TEST_USER)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]
    assert "id" in data

def test_duplicate_username_registration():
    """Тест попытки регистрации с существующим именем пользователя"""
    response = client.post("/register/", json=TEST_USER)
    assert response.status_code == 401
    assert "username already registered" in response.json()["detail"]

def test_duplicate_email_registration():
    """Тест попытки регистрации с существующим email"""
    duplicate_user = TEST_USER.copy()
    duplicate_user["username"] = "new_username"
    response = client.post("/register/", json=duplicate_user)
    assert response.status_code == 401
    assert "email already registered" in response.json()["detail"]

def test_login_success():
    """Тест успешной аутентификации"""
    global access_token
    response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    access_token = data["access_token"]

def test_login_invalid_password():
    """Тест аутентификации с неверным паролем"""
    response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_users():
    """Тест получения списка пользователей"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0
    assert any(user["username"] == TEST_USER["username"] for user in users)

def test_get_current_user():
    """Тест получения информации о текущем пользователе"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == TEST_USER["username"]
    assert user["email"] == TEST_USER["email"]

def test_update_user():
    """Тест обновления информации о пользователе"""
    headers = {"Authorization": f"Bearer {access_token}"}
    new_data = {"full_name": "Updated Name", "email": "updated@example.com"}
    response = client.put("/users/me", headers=headers, json=new_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == new_data["full_name"]
    assert updated_user["email"] == new_data["email"]

def test_delete_user():
    """Тест удаления пользователя"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/users/me", headers=headers)
    assert response.status_code == 200
    # Попытка повторного входа должна провалиться
    response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert response.status_code == 401
    # Сбрасываем токен, так как пользователь удален
    global access_token
    access_token = None