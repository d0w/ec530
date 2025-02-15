from pydantic import BaseModel, Field
from typing import Optional
from src.models.room import RoomType

class RoomBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    floor: Optional[int] = None
    sqft: Optional[int] = Field(None, gt=0)
    house_id: int = Field(..., gt=0)
    type: Optional[RoomType] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    floor: Optional[int] = Field(None, ge=0)
    sqft: Optional[int] = Field(None, gt=0)
    house_id: Optional[int] = Field(None, gt=0)
    type: Optional[RoomType] = None

class RoomResponse(RoomBase):
    id: int = Field(..., gt=0)

    # model_config = ConfigDict(from_attributes=True)