from fastapi import APIRouter, HTTPException, status
from src.models.room import Room
from src.schemas.room import RoomCreate, RoomUpdate
import logging
from src.api.utils.id_generator import IdGenerator

logger = logging.getLogger(__name__)
id_generator = IdGenerator()

router = APIRouter()

# In-memory storage for demonstration purposes
rooms = []

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(room: RoomCreate):
    # get next id
    new_id = id_generator.get_next_id()

    new_room = Room(id=new_id, **room.model_dump())
    rooms.append(new_room)
    logger.info(f"Room created: {new_room}")
    return {
        "message": "Room created",
        "room": new_room
    }

@router.get("/", status_code=status.HTTP_200_OK)
async def get_rooms():
    logger.info("Fetching all rooms")
    return rooms

@router.get("/{room_id}", status_code=status.HTTP_200_OK)
async def get_room(room_id: int):
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        logger.warning(f"Room with ID {room_id} not found")
        raise HTTPException(status_code=404, detail="Room not found")
    logger.info(f"Room fetched: {room}")
    return room

@router.put("/{room_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_room(room_id: int, room_update: RoomUpdate):
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        logger.warning(f"Room with ID {room_id} not found for update")
        raise HTTPException(status_code=404, detail="Room not found")
    for key, value in room_update.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    logger.info(f"Room updated: {room}")
    return {
        "message": "Room updated",
        "room": room
    }

@router.delete("/{room_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_room(room_id: int):
    for i, room in enumerate(rooms):
        if room.id == room_id:
            del rooms[i]
            logger.info(f"Room with ID {room_id} deleted")
            return {"message": "Room deleted"}
    logger.warning(f"Room with ID {room_id} not found for deletion")
    raise HTTPException(status_code=404, detail="Room not found")