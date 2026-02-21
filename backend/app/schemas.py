import string
from pydantic import BaseModel
from datetime import datetime

class HairdresserCreate(BaseModel):
    first_name: str
    specialization: str

class HairdresserOut(BaseModel):
    first_name: str
    specialization: str
    is_active: bool
    id: int

    class Config:
        from_attributes: True

class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price: float

class ServiceOut(ServiceCreate):
    id: int

    class Config:
        from_attributes: True

class BookingCreate(BaseModel):
    hairdresser_id: int
    service_id: int
    client_name: str
    client_phone: str
    booking_datetime: datetime

class BookingOut(BookingCreate):
    status: str
    created_at: datetime
    id: int

    class Config:
        from_attributes = True
