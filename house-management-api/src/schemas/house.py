from pydantic import BaseModel, Field
from typing import List, Optional

# these are the schemas that will be used to validate the data coming from the client

class HouseBase(BaseModel):
    name: str = Field(min_length=5)
    address: str = Field(min_length=5)
    gps: List[float] # [latitude, longitude]
    owner: int
    occupants: Optional[List[str]] = []


class HouseCreate(HouseBase):
    pass

class HouseUpdate(HouseBase):
    name: Optional[str] = Field(None, min_length=5)
    address: Optional[str] = Field(None, min_length=5)
    gps: Optional[List[float]] = None
    owner: Optional[str] = None
    occupants: Optional[List[str]] = None

class HouseResponse(HouseBase):
    id: int

    # model_config = ConfigDict(from_attributes=True)