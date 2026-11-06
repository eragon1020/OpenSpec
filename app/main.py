from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import espacio as espacio_model  # noqa: F401
from app.routers import espacios


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Gestión de Espacios Académicos", lifespan=lifespan)
app.include_router(espacios.router)
