from fastapi import APIRouter, Request, HTTPException, Depends, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

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
def google_login(request: Request):
    print(f"\n[Login] User-Agent: {request.headers.get('user-agent')}")
    print(f"[Login] Sec-Purpose / Purpose: {request.headers.get('sec-purpose')} / {request.headers.get('purpose')}")
    print(f"[Login] Referer: {request.headers.get('referer')}")

    flow = google_oauth_service.create_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    response = RedirectResponse(url=authorization_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=300,
        path="/",
    )

    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    stored_state = request.cookies.get("oauth_state")

    print(f"[OAuth] stored_state from cookie: {stored_state!r}")
    print(f"[OAuth] state from Google:         {state!r}")
    print(f"[OAuth] all cookies:               {dict(request.cookies)}")

    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    try:
        # 1. Exchange authorization code (sync Google lib — run in threadpool)
        credentials = await run_in_threadpool(
            google_oauth_service.exchange_code,
            code=code,
            state=state,
        )

        # 2. Get Google user information (sync — threadpool)
        user_info = await run_in_threadpool(
            google_oauth_service.get_user_info,
            credentials,
        )

        # 3. Get/create user in database
        user = await user_service.get_or_create_google_user(
            db=db,
            user_info=user_info,
            credentials=credentials,
        )

        # 4. Setup Google Drive (sync — threadpool)
        folders = await run_in_threadpool(
            google_drive_service.setup_user_drive,
            user,
        )

        user.framefind_folder_id = folders["framefind"]["id"]

        # 5. Commit and refresh
        await db.commit()
        await db.refresh(user)

        # 6. Create JWT
        access_token = create_access_token(data={"sub": str(user.id)})

    except Exception as e:
        print(f"Google authentication error: {e}")
        raise

    response = RedirectResponse(url=f"{settings.BACKEND_URL}/docs")

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
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/logout")
def logout():
    response = Response(
        content="Logged out successfully",
        status_code=status.HTTP_204_NO_CONTENT,
    )

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    return response

