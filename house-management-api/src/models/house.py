from typing import List, Optional

# these are actual objects that will be stored in the database

class House:
    def __init__(
        self, 
        id: int, 
        name: str, 
        address: str, 
        gps: List[float], 
        owner: str,
        occupants: Optional[List[str]] = None
    ):
        self.id = id
        self.name = name
        self.address = address
        self.gps = gps  # Should be [latitude, longitude]
        self.owner = owner
        self.occupants = occupants or []

    def remove_occupant(self, occupant: str):
        if occupant in self.occupants:
            self.occupants.remove(occupant)

    def __str__(self):
        return f"House(id={self.id}, name={self.name}, address={self.address}, owner={self.owner})"
    