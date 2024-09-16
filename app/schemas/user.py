from pydantic import BaseModel

class UserBase(BaseModel):
    telegram_id: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    telegram_id: str
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # Необходимо для поддержки from_orm в Pydantic 2.x

class UserWithToken(BaseModel):
    access_token: str
    token_type: str
    user: User

    class Config:
        from_attributes = True
