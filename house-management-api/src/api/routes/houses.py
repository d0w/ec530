from fastapi import APIRouter, HTTPException
from src.models.house import House
from src.schemas.house import HouseCreate, HouseUpdate

router = APIRouter()

# In-memory storage for demonstration purposes
houses = []

@router.get("/houses", response_model=list[House])
async def get_houses():
    return houses

@router.post("/houses", response_model=House)
async def create_house(house: HouseCreate):
    new_house = House(**house.dict())
    houses.append(new_house)
    return new_house

@router.get("/houses/{house_id}", response_model=House)
async def get_house(house_id: int):
    house = next((h for h in houses if h.id == house_id), None)
    if house is None:
        raise HTTPException(status_code=404, detail="House not found")
    return house

@router.put("/houses/{house_id}", response_model=House)
async def update_house(house_id: int, house: HouseUpdate):
    existing_house = next((h for h in houses if h.id == house_id), None)
    if existing_house is None:
        raise HTTPException(status_code=404, detail="House not found")
    for key, value in house.dict(exclude_unset=True).items():
        setattr(existing_house, key, value)
    return existing_house

@router.delete("/houses/{house_id}", status_code=204)
async def delete_house(house_id: int):
    global houses
    houses = [h for h in houses if h.id != house_id]
    return