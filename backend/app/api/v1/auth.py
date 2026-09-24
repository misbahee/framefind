from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db

router = APIRouter(
    prefix="/auth",
    tags={"Authentication"}
)


@router.get("")
def test(db: Session = Depends(get_db)):
    return {"message": " This end point is working even after the db session"}