from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.AdminUser).filter(models.AdminUser.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Wrong email")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_access_token({"sub": user.email})

    return {"access_token": token}