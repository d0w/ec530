from fastapi import APIRouter, HTTPException, status
from src.models.device import Device
from src.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
import logging
from src.api.utils.id_generator import IdGenerator

logger = logging.getLogger(__name__)
id_generator = IdGenerator()

router = APIRouter()

# In-memory storage for demonstration purposes
devices = []

@router.get("/", status_code=status.HTTP_200_OK)
async def get_devices():
    logger.info("Fetching all devices")
    return devices

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate):
    # get next id
    new_id = id_generator.get_next_id()
    new_device = Device(id=new_id, **device.model_dump())
    devices.append(new_device)
    logger.info(f"Device created: {new_device}")
    return new_device

@router.get("/{device_id}", status_code=status.HTTP_200_OK)
async def get_device(device_id: int):
    device = next((d for d in devices if d.id == device_id), None)
    if device is None:
        logger.warning(f"Device with ID {device_id} not found")
        raise HTTPException(status_code=404, detail="Device not found")
    logger.info(f"Device fetched: {device}")
    return device

@router.put("/{device_id}", status_code=status.HTTP_200_OK)
async def update_device(device_id: int, device: DeviceUpdate):
    existing_device = next((d for d in devices if d.id == device_id), None)
    if existing_device is None:
        logger.warning(f"Device with ID {device_id} not found for update")
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in device.model_dump(exclude_unset=True).items():
        setattr(existing_device, key, value)
    logger.info(f"Device updated: {existing_device}")
    return existing_device

@router.delete("/{device_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_device(device_id: int):
    for i, device in enumerate(devices):
        if device.id == device_id:
            del devices[i]
            logger.info(f"Device with ID {device_id} deleted")
            return {"message": "Device deleted"}
    logger.warning(f"Device with ID {device_id} not found for deletion")
    raise HTTPException(status_code=404, detail="Device not found")