import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_houses():
    response = client.get("/houses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_house():
    response = client.post("/houses", json={"id": 1, "address": "123 Main St", "owner": "John Doe"})
    assert response.status_code == 201
    assert response.json()["address"] == "123 Main St"

def test_get_house():
    response = client.get("/houses/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_house():
    response = client.put("/houses/1", json={"address": "456 Elm St"})
    assert response.status_code == 200
    assert response.json()["address"] == "456 Elm St"

def test_delete_house():
    response = client.delete("/houses/1")
    assert response.status_code == 204
    response = client.get("/houses/1")
    assert response.status_code == 404