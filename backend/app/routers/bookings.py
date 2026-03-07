from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from app.schemas import BookingCreate, BookingOut
from app.security import get_current_admin
from typing import List
from datetime import date
import math
import random

router = APIRouter()

@router.post("/bookings", response_model=BookingOut)
def create_booking(data:BookingCreate, db: Session = Depends(get_db)):
    booking = models.Booking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/bookings/any-hairdresser", response_model=BookingOut)
def create_booking_any_hairdresser(data: BookingCreate, db: Session = Depends(get_db)):
    hairdressers = db.query(models.Hairdresser).filter(
        models.Hairdresser.is_active == True 
    ).all()

    free_hairdressers = []
    for hairdresser in hairdressers:
        occupied_hairdresser = db.query(models.Booking).filter(
            models.Booking.hairdresser_id == hairdresser.id,
            models.Booking.booking_datetime == data.booking_datetime 
        ).first()
        if not occupied_hairdresser:
            free_hairdressers.append(hairdresser)
    if not free_hairdressers:
        raise HTTPException(status_code=400, detail="Niestety brak wolnych fryzjerów w wybranym terminie")

    selected_barber = random.choice(free_hairdressers)
    data.hairdresser_id = selected_barber.id

    booking = models.Booking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

ALL_HOURS = [
    "08:00","08:30","09:00","09:30","10:00","10:30",
    "11:00","11:30","12:00","12:30","13:00","13:30",
    "14:00","14:30","15:00","15:30","16:00","16:30",
    "17:00","17:30","18:00","18:30"
]
@router.get("/available-slots")
def get_available_slots(hairdresser_id: int, date: date, service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    duration = service.duration_minutes if service else 30
   
    occupied = db.query(
        models.Booking.booking_datetime,
        models.Service.duration_minutes
    ).join(
        models.Service, models.Booking.service_id == models.Service.id
    ).filter(
        models.Booking.hairdresser_id == hairdresser_id,
        func.date(models.Booking.booking_datetime) == date,
        models.Booking.status != "cancelled"
    ).all()

    occupied_slots = set()
    for booking_time, booking_duration in occupied:
        slots = math.ceil(booking_duration / 30)
        hour = booking_time.strftime("%H:%M")
        idx = ALL_HOURS.index(hour) if hour in ALL_HOURS else -1
        for i in range(slots):
            if idx + i < len(ALL_HOURS):
                occupied_slots.add(ALL_HOURS[idx + i])

    slots_needed = duration // 30
    free_hours = []
    for i, hour in enumerate(ALL_HOURS):
        if hour not in occupied_slots:
            if i + slots_needed <= len(ALL_HOURS):
                slots = ALL_HOURS[i:i + slots_needed]
                if not any(s in occupied_slots for s in slots):
                    free_hours.append(hour)

    return {"free_hours": free_hours}



@router.get("/admin/bookings", response_model=List[BookingOut])
def get_bookings(db: Session=Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Booking).all()

@router.patch("/admin/bookings/{id}")
def update_booking_status(id: int, status: str, db: Session=Depends(get_db), admin=Depends(get_current_admin)):
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Nie znaleziono rezerwacji")
    booking.status = status
    db.commit()
    return {"message": "Status zaktualizowany"}