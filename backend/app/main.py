from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import auth, hairdressers, services, bookings
from app.database import Base, engine
from app import models

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})

app.include_router(auth.router)
app.include_router(hairdressers.router)
app.include_router(services.router)
app.include_router(bookings.router)