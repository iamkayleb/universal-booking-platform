from datetime import datetime
from pydantic import BaseModel

class BusinessCreate(BaseModel):
    name: str
    industry: str
# What we expect when creating a user
class UserCreate(BaseModel):
    email: str
    password: str
    business: BusinessCreate

# What we send back to the user (we don't want to send the password!)
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    duration: int  # in minutes
    price: int
    
class ServiceResponse(ServiceCreate):
    id: int
    business_id: int
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    start_time: datetime  # ISO format datetime string
    service_id: int
class BookingResponse(BookingCreate):
    id: int
    user_id: int
    end_time: datetime
    class Config:
        from_attributes = True

# ... existing schemas ...

class Token(BaseModel):
    access_token: str
    token_type: str