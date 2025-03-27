import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.device import DeviceType, DeviceStatus
import logging

logger = logging.getLogger(__name__)
client = TestClient(app)

# chatgpt used to enhance original test cases to improve coverage
@pytest.fixture(autouse=True)
def clear_devices():
    logger.info("Setting up - clearing devices before test")
    from src.api.routes.devices import devices
    devices.clear()
    yield
    logger.info("Tearing down - clearing devices after test")
    devices.clear()

def test_create_device_success():
    device_data = {
        "name": "Living Room Light",
        "room_id": 1,
        "device_type": DeviceType.LIGHT.value,
        "status": DeviceStatus.OFF.value,
        "settings": {"brightness": 0}
    }
    response = client.post("/api/devices", json=device_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == device_data["name"]
    assert data["room_id"] == device_data["room_id"]
    assert data["device_type"] == device_data["device_type"]
    assert "id" in data

def test_create_device_invalid_data():
    # Test with missing required fields
    invalid_device = {
        "name": "Test Device"
        # missing room_id and device_type
    }
    response = client.post("/api/devices", json=invalid_device)
    assert response.status_code == 422

    # Test with invalid device type
    invalid_type = {
        "name": "Test Device",
        "room_id": 1,
        "device_type": "invalid_type",
        "status": DeviceStatus.OFF.value
    }
    response = client.post("/api/devices", json=invalid_type)
    assert response.status_code == 422

def test_get_devices():
    # First create a device
    device_data = {
        "name": "Thermostat",
        "room_id": 1,
        "device_type": DeviceType.THERMOSTAT.value,
        "status": DeviceStatus.ON.value,
        "settings": {"temperature": 72}
    }
    client.post("/api/devices/", json=device_data)
    
    response = client.get("/api/devices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_device_by_id():
    # First create a device
    device_data = {
        "name": "Motion Sensor",
        "room_id": 1,
        "device_type": DeviceType.SENSOR.value,
        "status": DeviceStatus.ON.value,
        "settings": {"sensitivity": "high"}
    }
    create_response = client.post("/api/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    response = client.get(f"/api/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["id"] == device_id
    assert response.json()["name"] == device_data["name"]

def test_get_nonexistent_device():
    response = client.get("/api/devices/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

def test_update_device():
    # First create a device
    device_data = {
        "name": "Smart Light",
        "room_id": 1,
        "device_type": DeviceType.LIGHT.value,
        "status": DeviceStatus.OFF.value,
        "settings": {"brightness": 50}
    }
    create_response = client.post("/api/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Update the device
    update_data = {
        "name": "Updated Light",
        "status": DeviceStatus.ON.value,
        "settings": {"brightness": 100}
    }
    response = client.put(f"/api/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["status"] == update_data["status"]
    assert data["settings"] == update_data["settings"]
    # Check that other fields remain unchanged
    assert data["room_id"] == device_data["room_id"]
    assert data["device_type"] == device_data["device_type"]

def test_update_nonexistent_device():
    update_data = {
        "name": "Updated Device",
        "status": DeviceStatus.ON.value
    }
    response = client.put("/api/devices/9999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

def test_delete_device():
    # First create a device
    device_data = {
        "name": "Test Device",
        "room_id": 1,
        "device_type": DeviceType.SENSOR.value,
        "status": DeviceStatus.ON.value
    }
    create_response = client.post("/api/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Delete the device
    response = client.delete(f"/api/devices/{device_id}")
    assert response.status_code == 202
    
    # Verify the device is deleted
    get_response = client.get(f"/api/devices/{device_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_device():
    response = client.delete("/api/devices/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

def test_device_status_transitions():
    # Create device with initial status
    device_data = {
        "name": "Status Test Device",
        "room_id": 1,
        "device_type": DeviceType.LIGHT.value,
        "status": DeviceStatus.OFF.value
    }
    response = client.post("/api/devices/", json=device_data)
    device_id = response.json()["id"]
    
    # Test all valid status transitions
    for status in DeviceStatus:
        update_data = {"status": status.value}
        response = client.put(f"/api/devices/{device_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["status"] == status.value

def test_device_settings_update():
    # Create device with initial settings
    device_data = {
        "name": "Settings Test Device",
        "room_id": 1,
        "device_type": DeviceType.THERMOSTAT.value,
        "status": DeviceStatus.ON.value,
        "settings": {"temperature": 70, "mode": "auto"}
    }
    response = client.post("/api/devices/", json=device_data)
    device_id = response.json()["id"]
    
    # Update settings
    new_settings = {"temperature": 72, "mode": "heat", "fan": "high"}
    update_data = {"settings": new_settings}
    response = client.put(f"/api/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["settings"] == new_settings