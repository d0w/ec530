from dataclasses import dataclass
from typing import List, Dict
from uuid import UUID, uuid4
from enum import Enum

# Device
# - type
# - name
# - room
# - settings
# - data
# - status

class DeviceStatus(Enum):
    on = 1
    off = 2

class DeviceType(Enum):
    light = 1
    thermostat = 2
    door = 3
    window = 4
    camera = 5
    lock = 6
    motion_sensor = 7
    smoke_detector = 8
    co2_detector = 9

class Device:
    id: UUID
    name: str
    room_id: UUID
    type: DeviceType
    status: DeviceStatus
    data: Dict[str, str]
    settings: Dict[str, str]

    def __init__(self, name: str, room_id: UUID, type: DeviceType):
        self.id = uuid4()
        self.name = name
        self.room_id = room_id
        self.type = type
        self.status = DeviceStatus.off
        self.data = {}
        self.settings = {}