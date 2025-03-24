from fastapi import APIRouter, HTTPException, Query, status
from src.models.house import House
from src.schemas.house import HouseCreate, HouseUpdate, HouseResponse
import logging
from src.api.utils.id_generator import IdGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

id_generator = IdGenerator()



# In-memory storage for demonstration purposes
houses = []

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[HouseResponse])
async def get_houses():
    logger.info("Fetching all houses")
    return houses

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=HouseResponse)
async def create_house(house: HouseCreate):

    # get next id
    new_id = id_generator.get_next_id()

    # ideally check owner id and use user id with session handler such as JWT cookies

    new_house = House(id=new_id, **house.model_dump())
    houses.append(new_house)
    logger.info(f"House created: {new_house}")
    return new_house

@router.get("/{house_id}", status_code=status.HTTP_200_OK, response_model=HouseResponse)
async def get_house(house_id: int):
    # auth middleware first

    house = next((h for h in houses if h.id == house_id), None)
    if house is None:
        logger.warning(f"House with ID {house_id} not found")
        raise HTTPException(status_code=404, detail="House not found")
    logger.info(f"House fetched: {house}")
    return house

@router.put("/{house_id}", status_code=status.HTTP_200_OK)
async def update_house(house_id: int, house: HouseUpdate):
    # auth middleware first
    
    existing_house = next((h for h in houses if h.id == house_id), None)
    if existing_house is None:
        logger.warning(f"House with ID {house_id} not found for update")
        raise HTTPException(status_code=404, detail="House not found")
    for key, value in house.model_dump(exclude_unset=True).items():
        setattr(existing_house, key, value)
    logger.info(f"House updated: {existing_house}")
    return existing_house

@router.delete("/{house_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_house(house_id: int):
    # auth middleware first
    
    for i, house in enumerate(houses):
        if house.id == house_id:
            del houses[i]
            logger.info(f"House with ID {house_id} deleted")
            return {"message": "House deleted"}
    logger.warning(f"House with ID {house_id} not found for deletion")
    raise HTTPException(status_code=404, detail="House not found")