from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models import User

router = APIRouter(
    prefix="/photos",
    tags=["Photos"],
)


@router.get("/{photo_id}")
async def show_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
