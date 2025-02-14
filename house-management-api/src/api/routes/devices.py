from fastapi import APIRouter, HTTPException
from src.models.device import Device
from src.schemas.device import DeviceCreate, DeviceUpdate

router = APIRouter()

# In-memory storage for demonstration purposes
devices = []

@router.get("/devices", response_model=list[Device])
async def get_devices():
    return devices

@router.post("/devices", response_model=Device)
async def create_device(device: DeviceCreate):
    new_device = Device(**device.dict())
    devices.append(new_device)
    return new_device

@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: int):
    device = next((d for d in devices if d.id == device_id), None)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/devices/{device_id}", response_model=Device)
async def update_device(device_id: int, device: DeviceUpdate):
    existing_device = next((d for d in devices if d.id == device_id), None)
    if existing_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in device.dict(exclude_unset=True).items():
        setattr(existing_device, key, value)
    return existing_device

@router.delete("/devices/{device_id}", response_model=dict)
async def delete_device(device_id: int):
    global devices
    devices = [d for d in devices if d.id != device_id]
    return {"message": "Device deleted"}