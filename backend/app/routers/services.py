from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import ServiceOut
from typing import List

router = APIRouter()

@router.get("/services", response_model=List[ServiceOut])
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()