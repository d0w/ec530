import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={"name": "John Doe", "email": "john@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"

def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user():
    response = client.post("/users", json={"name": "Jane Doe", "email": "jane@example.com"})
    user_id = response.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"

def test_update_user():
    response = client.post("/users", json={"name": "Jake Doe", "email": "jake@example.com"})
    user_id = response.json()["id"]
    response = client.put(f"/users/{user_id}", json={"name": "Jake Updated", "email": "jake_updated@example.com"})
    assert response.status_code == 200
    assert response.json()["name"] == "Jake Updated"

def test_delete_user():
    response = client.post("/users", json={"name": "Mark Doe", "email": "mark@example.com"})
    user_id = response.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404