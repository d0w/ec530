# Room
# - Name
# - floor
# - sqft
# - house
# - type
from typing import Optional
from enum import Enum

class RoomType(str, Enum):
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    KITCHEN = "kitchen"
    LIVING_ROOM = "living_room"
    DINING_ROOM = "dining_room"
    OFFICE = "office"
    GARAGE = "garage"
    BASEMENT = "basement"
    ATTIC = "attic"
    OTHER = "other"

class Room:
    def __init__(self, id: int, name: str, floor: Optional[int], sqft: Optional[int], house_id: int, type: Optional[RoomType]):
        self.id = id
        self.name = name
        self.floor = floor
        self.sqft = sqft
        self.house_id = house_id
        self.type = type
