from uuid import UUID, uuid4
from enum import Enum
from typing import List

class Role(Enum):
    admin = 1
    user = 2

class User:
    id: UUID
    name: str
    email: str
    role: Role
    houses: List[UUID]

    def __init__(self, name: str, email: str, role: Role):
        self.id = uuid4()
        self.name = name
        self.email = email
        self.role = role
        self.houses = []
    