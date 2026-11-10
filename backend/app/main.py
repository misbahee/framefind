from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import v1_router
from app.services.face_recognition import face_recognition_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: warm up the model and store the service instance on app.state
    face_recognition_service._load()
    app.state.face_recognition = face_recognition_service

    yield

    # shutdown
    app.state.face_recognition = None


app = FastAPI(lifespan= lifespan)


app.include_router(
    v1_router,
    prefix= "/api"
    )

