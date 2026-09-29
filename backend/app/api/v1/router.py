from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import events

v1_router = APIRouter(
    prefix="/v1"
)

v1_router.include_router(auth.router)
v1_router.include_router(events.router)