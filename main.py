from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.router import router as v1_router
from core.cors import setup_cors
from db.database import create_db_and_tables
# db/database.py
from models.user_model import User  # noqa: F401
from models.todo_model import Refrigerador, Alimento  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Mike API", version="1.0.0", lifespan=lifespan)
setup_cors(app)
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "¡Bienvenido a FastAPI Mike!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
