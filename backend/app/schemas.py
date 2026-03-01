import string
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HairdresserCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    specialization: Optional[str] = None

class HairdresserOut(BaseModel):
    first_name: str
    specialization: Optional[str] = None
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
    notes: Optional[str] = None

class BookingOut(BookingCreate):
    status: str
    created_at: datetime
    id: int
    notes: Optional[str] = None

    class Config:
        from_attributes = True
