from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings


class GoogleOAuthService:

    def create_flow(self) -> Flow:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        settings.GOOGLE_REDIRECT_URI,
                    ],
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/drive.file",
            ],
            autogenerate_code_verifier=False,
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        return flow


    def exchange_code(
        self,
        code: str,
        state: str,
    ):
        flow = self.create_flow()

        flow.state = state

        flow.fetch_token(code=code)

        return flow.credentials

    def get_user_info(self, credentials):
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        return {
            "google_user_id": id_info["sub"],
            "email": id_info["email"],
            "name": id_info.get("name"),
            "google_profile_photo": id_info.get("picture"),
        }


google_oauth_service = GoogleOAuthService()