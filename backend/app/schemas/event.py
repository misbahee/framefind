from datetime import date
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class EventCreate(BaseModel):
    name: str
    date: date
    location: str | None = None
    description: str | None = None


class EventResponse(BaseModel):
    id: UUID
    name: str
    date: date
    location: str | None
    description: str | None
    drive_folder_id: str
    invitation_token: str
    status: str

    model_config = ConfigDict(from_attributes=True)