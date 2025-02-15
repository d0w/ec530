from fastapi import APIRouter, HTTPException, status
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserResponseWithMessage
import logging
from src.api.utils.id_generator import IdGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demonstration purposes
users = []

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponseWithMessage)
async def create_user(user: UserCreate):
    # add prevention for admin and duplicates
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    elif any(u.username == user.username for u in users):
        raise HTTPException(status_code=400, detail="Username already taken")


    # get next id
    new_id = IdGenerator().get_next_id()

    new_user = User(id=new_id, **user.model_dump())
    users.append(new_user)
    logger.info(f"User created: {new_user}")
    return {
        "message": "User created",
        "user": new_user
    }

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_users():
    logger.info("Fetching all users")
    return users

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user_id: int):
    user = next((u for u in users if u.id == user_id), None)
    if user is None:
        logger.warning(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User fetched: {user}")
    return user

@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponseWithMessage)
async def update_user(user_id: int, user_update: UserUpdate):
    user = next((u for u in users if u.id == user_id), None)
    if user is None:
        logger.warning(f"User with ID {user_id} not found for update")
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    logger.info(f"User updated: {user}")
    return {
        "message": "User updated",
        "user": user
    }

@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user.id == user_id:
            del users[i]
            logger.info(f"User with ID {user_id} deleted")
            return {"message": f"User {user_id} deleted"}
    logger.warning(f"User with ID {user_id} not found for deletion")
    raise HTTPException(status_code=404, detail="User not found")