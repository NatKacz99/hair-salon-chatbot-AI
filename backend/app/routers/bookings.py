from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import BookingCreate, BookingOut
from app.security import get_current_admin
from typing import List

router = APIRouter()

@router.post("/bookings", response_model=BookingOut)
def create_booking(data:BookingCreate, db: Session = Depends(get_db)):
    booking = models.Booking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

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