import secrets
from uuid import UUID
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Event, EventMembership

class EventService:

    def create_event(
        self,
        db: Session,
        owner_id,
        name: str,
        date,
        location: str | None,
        description: str | None,
        drive_folder_id: str,
    ):
        event = Event(
            owner_id=owner_id,
            name=name,
            date=date,
            location=location,
            description=description,
            drive_folder_id=drive_folder_id,
            invitation_token=secrets.token_urlsafe(32),
            status="CREATED",
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event


    def get_user_events(self, db: Session, user_id):
        """Finds all the event where the user is owner or member. """

        statement = (
            select(Event)
            .outerjoin(
                EventMembership,
                EventMembership.event_id == Event.id,
            )
            .where(
                or_(
                    Event.owner_id == user_id,
                    EventMembership.user_id == user_id,
                )
            )
            .distinct()
            .order_by(Event.created_at.desc())
        )

        return db.scalars(statement).all()


    def get_user_event(
        self,
        db: Session,
        event_id: UUID,
        user_id: UUID,
    ):
        """ Gives details about a specific event if the user is owner or the member. """

        statement = (
            select(Event)
            .outerjoin(
                EventMembership,
                EventMembership.event_id == Event.id,
            )
            .where(
                Event.id == event_id,
                or_(
                    Event.owner_id == user_id,
                    EventMembership.user_id == user_id,
                ),
            )
        )

        return db.scalar(statement)


    def get_invitation_link(
        self,
        db: Session,
        event_id: UUID,
        user_id: UUID,
    ):
        """ Return the invitation url of the event for the owner. """

        statement = (
            select(Event)
            .where(
                Event.id == event_id,
                Event.owner_id == user_id,
            )
        )

        event = db.scalar(statement)

        if event is None:
            return None

        return event.invitation_token


    def get_invitation(
        self,
        db: Session,
        invitation_token: str,
        user_id,
    ):
        """ Returns event details for the valid invitation token and the membership status. """
        
        statement = (
            select(Event, EventMembership)
            .outerjoin(
                EventMembership,
                (EventMembership.event_id == Event.id)
                & (EventMembership.user_id == user_id),
            )
            .where(Event.invitation_token == invitation_token)
        )

        result = db.execute(statement).one_or_none()

        if result is None:
            return None

        event, membership = result

        return {
            "event_id": event.id,
            "event_name": event.name,
            "date": event.date,
            "location": event.location,
            "description": event.description,
            "already_joined": (
                event.owner_id == user_id
                or membership is not None
            ),
        }

    def join_event(
        self,
        db: Session,
        event_id: UUID,
        user_id: UUID,
        invitation_token: str,
    ):
        # 1. Find the event
        event = db.get(Event, event_id)

        if event is None:
            return None, "event_not_found"

        # 2. Verify that the invitation token belongs to this event
        if event.invitation_token != invitation_token:
            return None, "invalid_invitation"

        # 3. Owner already has access
        if event.owner_id == user_id:
            return event, "already_joined"

        # 4. Check whether the user is already a member
        statement = select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == user_id,
        )

        membership = db.scalar(statement)

        if membership is not None:
            return event, "already_joined"

        # 5. Create membership
        membership = EventMembership(
            event_id=event_id,
            user_id=user_id,
        )

        db.add(membership)
        db.commit()
        db.refresh(membership)

        return event, "joined"
            


event_service = EventService()