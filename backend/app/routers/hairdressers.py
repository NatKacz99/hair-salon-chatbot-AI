from fastapi import APIRouter, Depends
from app.security import get_current_admin

router = APIRouter()

@router.get("/admin-test")
def admin_test(current_admin: str = Depends(get_current_admin)):
    return {"message": f"Hello {current_admin}"}