from pydantic import BaseModel


class EventJoinRequest(BaseModel):
    invitation_token: str
