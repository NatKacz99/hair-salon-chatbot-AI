from app.security import hash_password
from app.database import SessionLocal
from app import models

db = SessionLocal()

admin = models.AdminUser(
    email="natalia.kaczynska.programista@gmail.com",
    hashed_password=hash_password("qwerty12"),
    role="owner"
)

db.add(admin)
db.commit()
print("Admin utworzony!")
db.close()