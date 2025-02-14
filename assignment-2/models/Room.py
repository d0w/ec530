from uuid import UUID, uuid4
from enum import Enum
from typing import List

# Room
# - Name
# - floor
# - sqft
# - house
# - type

class RoomType(Enum):
    bedroom = 1
    bathroom = 2
    kitchen = 3
    living_room = 4
    dining_room = 5
    office = 6
    garage = 7
    basement = 8
    attic = 9

class Room:
    id: UUID
    name: str
    sqft: int
    house_id: UUID
    devices: List[UUID]
    type: RoomType

    def __init__(self, name: str, house_id: UUID, sqft: int, type: RoomType):
        self.id = uuid4()
        self.name = name
        self.house_id = house_id
        self.devices = []
        self.sqft = sqft