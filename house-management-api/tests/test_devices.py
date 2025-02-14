import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_device():
    response = client.post("/devices", json={"name": "Device 1", "room_id": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "Device 1"

def test_get_devices():
    response = client.get("/devices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_device():
    response = client.get("/devices/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_device():
    response = client.put("/devices/1", json={"name": "Updated Device 1"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Device 1"

def test_delete_device():
    response = client.delete("/devices/1")
    assert response.status_code == 204