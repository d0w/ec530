from dataclasses import dataclass
from typing import List, Dict
from uuid import UUID, uuid4

from Models.Room import Room

class House:
    id: UUID
    address: str
    name: str
    owner_id: UUID
    rooms: Dict[UUID, Room]
    tenants: List[UUID]  # references to user IDs

    def __init__(self, address: str, owner_id: UUID):
        self.id = uuid4()
        self.address = address
        self.owner_id = owner_id
        self.rooms = {}
        self.tenants = []