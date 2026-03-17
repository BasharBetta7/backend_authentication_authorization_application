from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

from app.schemas.user import UserRead


class EventBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    owner_id: int 
    date: datetime
    description: str = Field(min_length=1, max_length=255)


class EventCreate(EventBase):
    pass 

class EventRead(EventBase):
    owner: UserRead
    id: int
    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    name: str | None  = Field(default=None, min_length=1, max_length=100)
    date: datetime | None = None
    description: str | None = Field(default=None, min_length=1, max_length=255)


class EventDelete(BaseModel):
    id: int