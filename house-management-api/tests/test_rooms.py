import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_room():
    response = client.post("/rooms", json={"name": "Living Room", "house_id": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "Living Room"

def test_get_rooms():
    response = client.get("/rooms")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_room():
    response = client.get("/rooms/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_room():
    response = client.put("/rooms/1", json={"name": "Updated Living Room"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Living Room"

def test_delete_room():
    response = client.delete("/rooms/1")
    assert response.status_code == 204
    response = client.get("/rooms/1")
    assert response.status_code == 404