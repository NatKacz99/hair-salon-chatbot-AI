from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.security import verify_password, create_access_token, hash_password

router = APIRouter()

@router.post("/admin/register")
def register_admin(email: str, password: str, db: Session = Depends(get_db)):
    existing_admin = db.query(models.AdminUser).filter(
        models.AdminUser.email == email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    admin = models.AdminUser(
        email=email,
        hashed_password=hash_password(password),
        role="owner"
    )

    db.add(admin)
    db.commit()
    return {"message": "Admin utworzony"}

@router.post("/admin/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.AdminUser).filter(models.AdminUser.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Wrong email")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_access_token({"sub": user.email})

    return {"access_token": token}