from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    token: Optional[str] = None

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True

    class Config:
        orm_mode = True


class BruteForceTaskCreate(BaseModel):
    hash: str
    charset: str
    max_length: int


class BruteForceTaskResponse(BaseModel):
    task_id: str


class BruteForceTaskStatus(BaseModel):
    status: str
    progress: float
    result: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str 