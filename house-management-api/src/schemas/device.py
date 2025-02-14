from pydantic import BaseModel

class DeviceBase(BaseModel):
    name: str
    room_id: int
    device_type: str
    status: str

class Device(DeviceBase):
    id: int

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    name: str | None = None
    room_id: int | None = None
    device_type: str | None = None
    status: str | None = None

