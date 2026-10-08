from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import UploadFile
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import settings


class GoogleDriveService:

    def get_drive_service(self, user):
        """Create an authenticated Google Drive API client for a user."""

        credentials = Credentials(
            token=user.access_token,
            refresh_token=user.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=[
                "https://www.googleapis.com/auth/drive.file",
            ],
        )

        return build("drive", "v3", credentials=credentials)

    def find_folder(
        self,
        drive,
        name: str,
        parent_id: str | None = None,
    ):
        """Find an existing folder by name, optionally within a parent folder."""
        
        query = (
            f"name = '{name}' "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )

        if parent_id:
            query += f" and '{parent_id}' in parents"

        result = drive.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, parents)",
            pageSize=1,
        ).execute()

        files = result.get("files", [])

        return files[0] if files else None


    def create_folder(
        self,
        drive,
        name: str,
        parent_id: str | None = None,
    ):
        """Create a Google Drive folder, optionally inside a parent folder."""
        
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        if parent_id:
            metadata["parents"] = [parent_id]

        return drive.files().create(
            body=metadata,
            fields="id, name, parents",
        ).execute()


    def get_or_create_folder(
        self,
        drive,
        name: str,
        parent_id: str | None = None,
    ):
        """Return an existing folder or create it if it does not exist."""
        
        folder = self.find_folder(
            drive=drive,
            name=name,
            parent_id=parent_id,
        )

        if folder:
            return folder

        return self.create_folder(
            drive=drive,
            name=name,
            parent_id=parent_id,
        )

    def setup_user_drive(self, user):
        """
        Ensure the required FrameFind folder structure exists
        in the user's Google Drive.
        """
        
        drive = self.get_drive_service(user)

        framefind_folder = self.get_or_create_folder(
            drive=drive,
            name="FrameFind",
        )

        events_folder = self.get_or_create_folder(
            drive=drive,
            name="Events",
            parent_id=framefind_folder["id"],
        )

        gallery_folder = self.get_or_create_folder(
            drive=drive,
            name="My Gallery",
            parent_id=framefind_folder["id"],
        )

        return {
            "framefind": framefind_folder,
            "events": events_folder,
            "gallery": gallery_folder,
        }


    def create_event_folder(
        self,
        user,
        event_name: str
    ):
        """Create an event folder inside the user's FrameFind/Events folder."""
        drive = self.get_drive_service(user)

        events_folder = self.find_folder(
            drive=drive,
            name="Events",
            parent_id=user.framefind_folder_id,
        )

        if not events_folder:
            raise ValueError("Events folder not found")

        return self.create_folder(
            drive=drive,
            name=event_name,
            parent_id=events_folder["id"],
        )


    def upload_photo(
        self,
        user,
        file: UploadFile,
        parent_folder_id: str,
    ):
        """Upload an event photo to a Google Drive folder."""
        
        drive = self.get_drive_service(user)

        file_metadata = {
            "name": file.filename,
            "parents": [parent_folder_id],
        }

        media = MediaIoBaseUpload(
            file.file,
            mimetype=file.content_type,
            resumable=True,
        )

        return drive.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, mimeType, parents",
        ).execute()

google_drive_service = GoogleDriveService()


