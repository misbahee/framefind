from fastapi import APIRouter, Request , HTTPException, Depends ,Response 
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services.google_oauth import google_oauth_service
from app.services.user import user_service
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.google_drive import google_drive_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/google/login")
def google_login():
    flow = google_oauth_service.create_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    response = RedirectResponse(url=authorization_url)

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=300,
        path="/",
    )

    return response

@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    stored_state = request.cookies.get("oauth_state")

    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    try:
        credentials = google_oauth_service.exchange_code(
            code=code,
            state=state,
        )

        user_info = google_oauth_service.get_user_info(
            credentials
        )

        user = user_service.get_or_create_google_user(
            db=db,
            user_info=user_info,
            credentials=credentials,
        )

        folders = google_drive_service.setup_user_drive(user)

        user.framefind_folder_id = folders["framefind"]["id"]

        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

    except Exception as e:
        print(f"Google authentication error: {e}")
        raise

    response = RedirectResponse(
        url="http://localhost:8000/docs"
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=30 * 60,
        path="/",
    )

    response.delete_cookie("oauth_state")

    return response


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/logout")
def logout():
    response = Response(
        content="Logged out successfully",
        status_code=200,
    )

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    return response

