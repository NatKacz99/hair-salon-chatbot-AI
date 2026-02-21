from pydantic import BaseModel
from datetime import datetime

class HairdresserCreate(BaseModel):
    first_name: str
    specialization: str

class HairdresserOut(BaseModel):
    first_name: str
    specialization: str
    is_active: bool

    class Config:
        from_attributes: True

class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price: float

class ServiceOut(ServiceCreate):
    name: str
    duration_minutes: int
    price: float

    class Config:
        from_attributes: True
