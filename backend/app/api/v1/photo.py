from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models import User

router = APIRouter(
    prefix="/photos",
    tags=['Photos']
)


@router.get("/{photo_id}")
def show_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    pass


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    pass
