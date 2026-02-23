from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import HairdresserCreate, HairdresserOut
from app.security import get_current_admin
from typing import List

router = APIRouter()

@router.get("/hairdressers", response_model=List[HairdresserOut])
def get_hairdressers(db: Session = Depends(get_db)):
    return db.query(models.Hairdresser).filter(models.Hairdresser.is_active == True).all()

@router.post("/admin/hairdressers", response_model=HairdresserOut)
def add_hairdresser(data: HairdresserCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    hairdresser = models.Hairdresser(**data.dict())
    db.add(hairdresser)
    db.commit()
    db.refresh(hairdresser)
    return hairdresser

@router.delete("/admin/hairdressers/{id}")
def delete_hairdresser(id: int, db: Session=Depends(get_db), admin=Depends(get_current_admin)):
    hairdresser = db.query(models.Hairdresser).filter(models.Hairdresser.id == id).first()
    if not hairdresser:
        raise HTTPException(status_code=404, detail="Nie znaleziono fryzjera")
    hairdresser.is_active = False
    db.commit()
    return {"message": "Fryzjer usunięty"}
