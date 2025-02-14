from fastapi import APIRouter, HTTPException
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate

router = APIRouter()

# In-memory storage for demonstration purposes
users = []

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    new_user = User(**user.dict())
    users.append(new_user)
    return new_user

@router.get("/", response_model=list[User])
async def get_users():
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = next((u for u in users if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate):
    user = next((u for u in users if u.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    global users
    users = [u for u in users if u.id != user_id] 
    return {"message": "User deleted"}