from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from src.models.user import UserPrivilege

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    phone: Optional[str] = Field(None)
    privilege: UserPrivilege = Field(default=UserPrivilege.USER)
    # can add password later

    

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    username: Optional[str] = Field(None, min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None)
    privilege: Optional[UserPrivilege] = None

    # can add password later

class UserResponse(UserBase):
    id: int

    # model_config = ConfigDict(from_attributes=True)

class UserResponseWithMessage(BaseModel):
    message: str
    user: UserResponse