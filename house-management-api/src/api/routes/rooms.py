from fastapi import APIRouter, HTTPException
from src.models.room import Room
from src.schemas.room import RoomCreate, RoomUpdate

router = APIRouter()

# In-memory storage for demonstration purposes
rooms = []

@router.post("/rooms", response_model=Room)
async def create_room(room: RoomCreate):
    new_room = Room(**room.dict())
    rooms.append(new_room)
    return new_room

@router.get("/rooms", response_model=list[Room])
async def get_rooms():
    return rooms

@router.get("/rooms/{room_id}", response_model=Room)
async def get_room(room_id: int):
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/rooms/{room_id}", response_model=Room)
async def update_room(room_id: int, room_update: RoomUpdate):
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    for key, value in room_update.dict(exclude_unset=True).items():
        setattr(room, key, value)
    return room

@router.delete("/rooms/{room_id}", status_code=204)
async def delete_room(room_id: int):
    global rooms
    rooms = [r for r in rooms if r.id != room_id] 
    return {"message": "Room deleted"}