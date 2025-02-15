from pydantic import BaseModel
from src.models.device import DeviceType
from src.models.device import DeviceStatus

# Device
# - type
# - name
# - room
# - settings
# - data
# - status

class DeviceBase(BaseModel):
    name: str
    room_id: int
    device_type: DeviceType | None
    status: DeviceStatus | None
    settings: dict | None = None

class DeviceResponse(DeviceBase):
    id: int

    # model_config = ConfigDict(from_attributes=True)

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    name: str | None = None
    room_id: int | None = None
    device_type: DeviceType | None = None
    status: DeviceStatus | None = None
    settings: dict | None = None
