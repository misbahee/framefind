from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.invitation import InvitationResponse, InvitationLinkResponse
from app.services.event import event_service


router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"],
)


@router.get(
    "/{invitation_token}",
    response_model=InvitationResponse,
)
async def get_invitation(
    invitation_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invitation = await event_service.get_invitation(
        db=db,
        invitation_token=invitation_token,
        user_id=current_user.id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    return invitation


@router.get(
    "/events/{event_id}/link",
    response_model=InvitationLinkResponse,
)
async def get_invitation_link(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    invitation_token = await event_service.get_invitation_link(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if invitation_token is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    invite_url = f"{settings.FRONTEND_URL}/join/{invitation_token}"

    return {
        "invite_url": invite_url,
    }
