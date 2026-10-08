from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PhotoResponse(BaseModel):
    id: UUID
    drive_file_id: str
    filename: str
    mime_type: str
    processing_status: str

    model_config = ConfigDict(from_attributes=True)