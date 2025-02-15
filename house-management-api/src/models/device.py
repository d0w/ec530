from typing import Optional
from enum import Enum

# Device
# - type
# - name
# - room
# - settings
# - data
# - status

class DeviceStatus(str, Enum):
    ON = "on"
    OFF = "off"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class DeviceType(str, Enum):
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    SENSOR = "sensor"
    # etc.

class Device:
    def __init__(self, id: int, name: str, room_id: int, device_type: DeviceType, status: DeviceStatus, settings: dict = {}):
        self.id = id
        self.name = name
        self.room_id = room_id
        self.device_type = device_type
        self.status = status
        self.settings = settings
        self.data = []