from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import events
from app.api.v1 import invitations
from app.api.v1 import photo

v1_router = APIRouter(
    prefix="/v1"
)

v1_router.include_router(auth.router)
v1_router.include_router(events.router)
v1_router.include_router(invitations.router)
v1_router.include_router(photo.router)