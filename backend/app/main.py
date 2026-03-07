from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, hairdressers, services, bookings, chat
from app.database import Base, engine
from app import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})

app.include_router(auth.router)
app.include_router(hairdressers.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(chat.router)