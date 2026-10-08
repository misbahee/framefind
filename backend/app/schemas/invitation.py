from datetime import date
from uuid import UUID

from pydantic import BaseModel


class InvitationResponse(BaseModel):
    event_id: UUID
    event_name: str
    date: date
    location: str | None
    description: str | None
    already_joined: bool

class InvitationLinkResponse(BaseModel):
    invite_url: str