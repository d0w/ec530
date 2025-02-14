from pydantic import BaseModel

class RoomBase(BaseModel):
    name: str
    floor: int
    house_id: int

class Room(RoomBase):
    id: int

class RoomCreate(RoomBase):
    pass

class RoomUpdate(RoomBase):
    name: str | None = None
    floor: int | None = None
    house_id: int | None = None

