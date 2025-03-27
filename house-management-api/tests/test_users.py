import pytest
from fastapi.testclient import TestClient
from src.main import app
import logging

logger = logging.getLogger(__name__)
client = TestClient(app)

# chatgpt used to enhance original test cases to improve coverage
@pytest.fixture(autouse=True)
def clear_users():
    logger.info("Setting up - clearing users before test")
    from src.api.routes.users import users
    users.clear()
    yield
    logger.info("Tearing down - clearing users after test")
    users.clear()

def test_create_user_success():
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["name"] == user_data["name"]
    assert data["user"]["username"] == user_data["username"]
    assert data["user"]["email"] == user_data["email"]
    assert "id" in data["user"]

def test_create_user_duplicate_email():
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    # Create first user
    client.post("/api/users/", json=user_data)
    
    # Try to create user with same email
    user_data["username"] = "johndoe2"
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_create_user_duplicate_username():
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    # Create first user
    client.post("/api/users/", json=user_data)
    
    # Try to create user with same username
    user_data["email"] = "john2@example.com"
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"

def test_create_user_invalid_data():
    # Test invalid email
    invalid_email = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "invalid-email",
        "phone": "+12345678901",
        "privilege": "user"
    }
    response = client.post("/api/users/", json=invalid_email)
    assert response.status_code == 422

    # Test invalid phone
    # invalid_phone = {
    #     "name": "John Doe",
    #     "username": "johndoe",
    #     "email": "john@example.com",
    #     "phone": "invalid-phone",
    #     "privilege": "user"
    # }
    # response = client.post("/api/users/", json=invalid_phone)
    # assert response.status_code == 422

def test_get_users():
    # Create a test user
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    client.post("/api/users/", json=user_data)
    
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_user_by_id():
    # Create a test user
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["user"]["id"]
    
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == user_data["username"]

def test_get_nonexistent_user():
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_update_user():
    # Create a test user
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["user"]["id"]
    
    # Update the user
    update_data = {
        "name": "John Updated",
        "phone": "+12345678902"
    }
    response = client.put(f"/api/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["user"]["name"] == update_data["name"]
    assert response.json()["user"]["phone"] == update_data["phone"]
    # Check that other fields remain unchanged
    assert response.json()["user"]["email"] == user_data["email"]

def test_update_nonexistent_user():
    update_data = {
        "name": "John Updated"
    }
    response = client.put("/api/users/9999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_delete_user():
    # Create a test user
    user_data = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "+12345678901",
        "privilege": "user"
    }
    create_response = client.post("/api/users/", json=user_data)
    user_id = create_response.json()["user"]["id"]
    
    # Delete the user
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 202
    
    # Verify the user is deleted
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_user():
    response = client.delete("/api/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"