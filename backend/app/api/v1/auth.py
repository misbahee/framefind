from fastapi import APIRouter, Request , HTTPException, Depends ,Response , status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
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

import time

@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    callback_start = time.perf_counter()
    print("\n========== GOOGLE CALLBACK START ==========")

    stored_state = request.cookies.get("oauth_state")

    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    try:
        # 1. Exchange authorization code
        start = time.perf_counter()

        credentials = google_oauth_service.exchange_code(
            code=code,
            state=state,
        )

        print(
            f"exchange_code: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        # 2. Get Google user information
        start = time.perf_counter()

        user_info = google_oauth_service.get_user_info(
            credentials
        )

        print(
            f"get_user_info: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        # 3. Get/create user in database
        start = time.perf_counter()

        user = user_service.get_or_create_google_user(
            db=db,
            user_info=user_info,
            credentials=credentials,
        )

        print(
            f"get_or_create_google_user: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        # 4. Setup Google Drive
        start = time.perf_counter()

        folders = google_drive_service.setup_user_drive(user)

        print(
            f"setup_user_drive: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        user.framefind_folder_id = folders["framefind"]["id"]

        # 5. Commit database
        start = time.perf_counter()

        db.commit()

        print(
            f"db.commit: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        # 6. Refresh database object
        start = time.perf_counter()

        db.refresh(user)

        print(
            f"db.refresh: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

        # 7. Create JWT
        start = time.perf_counter()

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        print(
            f"create_access_token: "
            f"{time.perf_counter() - start:.3f} seconds"
        )

    except Exception as e:
        print(f"Google authentication error: {e}")
        raise

    print(
        f"TOTAL CALLBACK PROCESSING: "
        f"{time.perf_counter() - callback_start:.3f} seconds"
    )

    response = RedirectResponse(
        url=f"{settings.BACKEND_URL}/docs"
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
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
        status_code=status.HTTP_204_NO_CONTENT
    )

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    return response

