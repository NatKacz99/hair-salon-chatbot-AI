from fastapi import FastAPI
from app.routers import auth, hairdressers

app = FastAPI()

app.include_router(auth.router)
app.include_router(hairdressers.router)