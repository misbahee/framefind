from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserService:

    def get_or_create_google_user(
        self,
        db: Session,
        user_info: dict,
        credentials,
    ) -> User:
        
        statement = select(User).where(User.google_user_id == user_info["google_user_id"])
        user = (
            db.scalar(statement)
        )

        if user is None:
            user = User(
                google_user_id=user_info["google_user_id"],
                email=user_info["email"],
                name=user_info["name"],
                google_profile_photo=user_info["google_profile_photo"],
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
            )

            db.add(user)

        else:
            user.email = user_info["email"]
            user.name = user_info["name"]
            user.google_profile_photo = user_info["google_profile_photo"]

            user.access_token = credentials.token
            user.token_expiry = credentials.expiry

            if credentials.refresh_token:
                user.refresh_token = credentials.refresh_token

        db.commit()
        db.refresh(user)

        return user


user_service = UserService()