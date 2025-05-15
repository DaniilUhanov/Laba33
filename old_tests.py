import pytest
from fastapi.testclient import TestClient
from main import app
from models import User
from database import SessionLocal
from security import hash_password

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(test_db):
    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": hash_password("testpassword"),
        "disabled": False
    }
    user = User(**user_data)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    # Get auth token for the test user
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_users(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_user():
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "full_name": "Test User",
        "password": "securePassword123!"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201  # Changed to 201 for created resources
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data

def test_login_success(test_user):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_login_invalid_password(test_user):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_current_user(auth_token, test_user):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email

def test_update_user(auth_token, test_user):
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {
        "email": "updated@example.com",
        "full_name": "Updated Name"
    }
    response = client.put(
        f"/users/{test_user.id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["full_name"] == update_data["full_name"]

def test_delete_user(auth_token, test_user, test_db):
    # First create a user to delete
    user_data = {
        "username": "todelete",
        "email": "delete@example.com",
        "hashed_password": hash_password("testpassword"),
        "disabled": False
    }
    user = User(**user_data)
    test_db.add(user)
    test_db.commit()
    
    # Now delete the user
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete(
        f"/users/{user.id}",
        headers=headers
    )
    assert response.status_code == 200
    
    # Verify deletion
    deleted_user = test_db.query(User).filter(User.id == user.id).first()
    assert deleted_user is None