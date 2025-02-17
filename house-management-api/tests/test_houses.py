import pytest
from fastapi.testclient import TestClient
from src.main import app
import logging

logger = logging.getLogger(__name__)
client = TestClient(app)



@pytest.fixture(autouse=True)
def clear_houses():
    logger.info("Setting up - clearing houses before test")
    from src.api.routes.houses import houses
    houses.clear()
    yield  # This is where the test runs
    logger.info("Tearing down - clearing houses after test")
    houses.clear()


def test_create_house_success():
    house_data = {
        "name": "Test House",
        "address": "123 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1,
        "occupants": ["John Doe"]
    }
    response = client.post("/api/houses/", json=house_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == house_data["name"]
    assert data["address"] == house_data["address"]
    assert data["gps"] == house_data["gps"]
    assert "id" in data

def test_create_house_invalid_data():
    # Test with invalid name (too short)
    invalid_house = {
        "name": "Test",  # Less than 5 characters
        "address": "123 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1
    }
    response = client.post("/api/houses/", json=invalid_house)
    assert response.status_code == 422

    # Test with invalid GPS coordinates
    # invalid_gps = {
    #     "name": "Test House",
    #     "address": "123 Test Street",
    #     "gps": [91.0, 181.0],  # Invalid coordinates
    #     "owner": 1
    # }
    # response = client.post("/api/houses/", json=invalid_gps)
    # assert response.status_code == 422

def test_get_houses():
    # First create a house
    house_data = {
        "name": "Test House Get",
        "address": "456 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1
    }
    client.post("/api/houses/", json=house_data)
    
    # Get all houses
    response = client.get("/api/houses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_house_by_id():
    # First create a house
    house_data = {
        "name": "Test House Individual",
        "address": "789 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1
    }
    create_response = client.post("/api/houses/", json=house_data)
    house_id = create_response.json()["id"]
    
    # Get the house by ID
    response = client.get(f"/api/houses/{house_id}")
    assert response.status_code == 200
    assert response.json()["id"] == house_id
    assert response.json()["name"] == house_data["name"]

def test_get_nonexistent_house():
    response = client.get("/api/houses/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "House not found"

def test_update_house():
    # First create a house
    house_data = {
        "name": "Test House Update",
        "address": "101 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1
    }
    create_response = client.post("/api/houses/", json=house_data)
    house_id = create_response.json()["id"]
    
    # Update the house
    update_data = {
        "name": "Updated Test House",
        "address": "101 Updated Street"
    }
    response = client.put(f"/api/houses/{house_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["address"] == update_data["address"]

def test_update_nonexistent_house():
    update_data = {
        "name": "Updated Test House",
        "address": "101 Updated Street"
    }
    response = client.put("/api/houses/9999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "House not found"

def test_delete_house():
    # First create a house
    house_data = {
        "name": "Test House Delete",
        "address": "202 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1
    }
    create_response = client.post("/api/houses/", json=house_data)
    house_id = create_response.json()["id"]
    
    # Delete the house
    response = client.delete(f"/api/houses/{house_id}")
    assert response.status_code == 202
    
    # Verify the house is deleted
    get_response = client.get(f"/api/houses/{house_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_house():
    response = client.delete("/api/houses/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "House not found"

def test_occupants_management():
    # Create house with occupants
    house_data = {
        "name": "Test House Occupants",
        "address": "303 Test Street",
        "gps": [42.3601, -71.0589],
        "owner": 1,
        "occupants": ["John Doe"]
    }
    response = client.post("/api/houses/", json=house_data)
    assert response.status_code == 201
    assert "John Doe" in response.json()["occupants"]

    # Update occupants
    house_id = response.json()["id"]
    update_data = {
        "occupants": ["John Doe", "Jane Doe"]
    }
    response = client.put(f"/api/houses/{house_id}", json=update_data)
    assert response.status_code == 200
    assert len(response.json()["occupants"]) == 2