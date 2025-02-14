from typing import Dict, List, Optional
from uuid import UUID
from ..models.House import House, Room
import json

class HouseController:
    def __init__(self):
        self.houses: Dict[UUID, House] = {}
    
    def create(self, house: House) -> House:
        json.loads(house)
        house = House(house., owner_id)
        self.houses[house.id] = house
        return json.dumps(house)
    
    def get(self, house_id: UUID) -> Optional[House]:
        return self.houses.get(house_id)
    
    def update(self, house_id: UUID, house: House) -> House:
        self.houses[house_id] = house
        return {
            "message": "House updated successfully",
            "house": house
        }
    
    def get_houses(self) -> List[House]:
        return list(self.houses.values())
    
    def add_room_to_house(self, house_id: UUID, room: Room) -> House:
        house = self.houses.get(house_id)
        if house is None:
            raise ValueError(f"House with ID {house_id} not found")
        house.rooms[room.id] = room
        return house
    
    def add_tenant_to_house(self, house_id: UUID, tenant_id: UUID) -> House:
        house = self.houses.get(house_id)
        if house is None:
            raise ValueError(f"House with ID {house_id} not found")
        house.tenants.append(tenant_id)
        return house