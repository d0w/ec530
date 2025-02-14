from pydantic import BaseModel

class HouseBase(BaseModel):
    address: str
    owner: str

class House(HouseBase):
    id: int

class HouseCreate(HouseBase):
    pass

class HouseUpdate(HouseBase):
    address: str | None = None
    owner: str | None = None