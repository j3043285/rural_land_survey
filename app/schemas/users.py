from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.users import UserRole

class UserBase(BaseModel):
    full_name: str
    email: str
    username: str
    role: UserRole = UserRole.SURVEYOR
    phone: Optional[str] = None
    badge_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
