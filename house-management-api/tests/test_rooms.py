import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.room import RoomType
import logging

logger = logging.getLogger(__name__)
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_rooms():
    logger.info("Setting up - clearing rooms before test")
    from src.api.routes.rooms import rooms
    rooms.clear()
    yield
    logger.info("Tearing down - clearing rooms after test")
    rooms.clear()

def test_create_room_success():
    room_data = {
        "name": "Master Bedroom",
        "floor": 2,
        "sqft": 250,
        "house_id": 1,
        "type": RoomType.BEDROOM.value
    }
    response = client.post("/api/rooms/", json=room_data)
    assert response.status_code == 201
    data = response.json()["room"]
    assert data["name"] == room_data["name"]
    assert data["floor"] == room_data["floor"]
    assert data["sqft"] == room_data["sqft"]
    assert data["type"] == room_data["type"]
    assert "id" in data

def test_create_room_invalid_data():
    # Test with missing required field
    invalid_room = {
        "name": "Master Bedroom",
        "floor": 2
        # missing house_id
    }
    response = client.post("/api/rooms/", json=invalid_room)
    assert response.status_code == 422

    # Test with invalid room type
    invalid_type = {
        "name": "Master Bedroom",
        "floor": 2,
        "sqft": 250,
        "house_id": 1,
        "type": "invalid_type"
    }
    response = client.post("/api/rooms/", json=invalid_type)
    assert response.status_code == 422

def test_get_rooms():
    # First create a room
    room_data = {
        "name": "Living Room",
        "floor": 1,
        "sqft": 300,
        "house_id": 1,
        "type": RoomType.LIVING_ROOM.value
    }
    client.post("/api/rooms/", json=room_data)
    
    response = client.get("/api/rooms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_room_by_id():
    # First create a room
    room_data = {
        "name": "Kitchen",
        "floor": 1,
        "sqft": 200,
        "house_id": 1,
        "type": RoomType.KITCHEN.value
    }
    create_response = client.post("/api/rooms/", json=room_data)
    room_id = create_response.json()["room"]["id"]
    
    response = client.get(f"/api/rooms/{room_id}")
    assert response.status_code == 200
    assert response.json()["id"] == room_id
    assert response.json()["name"] == room_data["name"]

def test_get_nonexistent_room():
    response = client.get("/api/rooms/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_update_room():
    # First create a room
    room_data = {
        "name": "Office",
        "floor": 2,
        "sqft": 150,
        "house_id": 1,
        "type": RoomType.OFFICE.value
    }
    create_response = client.post("/api/rooms/", json=room_data)
    room_id = create_response.json()["room"]["id"]
    
    # Update the room
    update_data = {
        "name": "Home Office",
        "sqft": 180
    }
    response = client.put(f"/api/rooms/{room_id}", json=update_data)
    assert response.status_code == 202
    data = response.json()["room"]
    assert data["name"] == update_data["name"]
    assert data["sqft"] == update_data["sqft"]
    # Check that other fields remain unchanged
    assert data["floor"] == room_data["floor"]
    assert data["type"] == room_data["type"]

def test_update_nonexistent_room():
    update_data = {
        "name": "Updated Room"
    }
    response = client.put("/api/rooms/9999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_delete_room():
    # First create a room
    room_data = {
        "name": "Guest Room",
        "floor": 2,
        "sqft": 180,
        "house_id": 1,
        "type": RoomType.BEDROOM.value
    }
    create_response = client.post("/api/rooms/", json=room_data)
    room_id = create_response.json()["room"]["id"]
    
    # Delete the room
    response = client.delete(f"/api/rooms/{room_id}")
    assert response.status_code == 202
    
    # Verify the room is deleted
    get_response = client.get(f"/api/rooms/{room_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_room():
    response = client.delete("/api/rooms/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Room not found"

def test_room_type_validation():
    for room_type in RoomType:
        room_data = {
            "name": f"{room_type.value} Room",
            "floor": 1,
            "sqft": 150,
            "house_id": 1,
            "type": room_type.value
        }
        response = client.post("/api/rooms/", json=room_data)
        assert response.status_code == 201
        assert response.json()["room"]["type"] == room_type.value