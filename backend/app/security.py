from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=60)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise Exception()
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")