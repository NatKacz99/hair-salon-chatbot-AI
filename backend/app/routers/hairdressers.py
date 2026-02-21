from fastapi import APIRouter, Depends
from app.security import get_current_admin

router = APIRouter()