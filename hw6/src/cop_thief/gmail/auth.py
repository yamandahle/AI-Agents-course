"""OAuth2 credential loading, refresh, and first-run browser flow for Gmail."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]


class GmailAuth:
    """Loads, refreshes, or creates OAuth2 credentials for the Gmail API."""

    def __init__(self, credentials_file: str, token_file: str):
        self._credentials_file = credentials_file
        self._token_file = token_file

    def get_credentials(self) -> Credentials:
        """Return valid Credentials, refreshing or re-authenticating as needed."""
        creds = self._load_token()
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = self._run_browser_flow()
        self._save_token(creds)
        return creds

    def _load_token(self) -> Credentials | None:
        """Load saved credentials from token_file, if it exists."""
        if not Path(self._token_file).exists():
            return None
        return Credentials.from_authorized_user_file(self._token_file, SCOPES)

    def _run_browser_flow(self) -> Credentials:
        """Run the first-time OAuth consent flow via a local browser window."""
        if not Path(self._credentials_file).exists():
            raise FileNotFoundError(
                f"Gmail credentials file not found: {self._credentials_file}"
            )
        flow = InstalledAppFlow.from_client_secrets_file(self._credentials_file, SCOPES)
        return flow.run_local_server(port=0)

    def _save_token(self, creds: Credentials) -> None:
        """Persist refreshed/new credentials to token_file."""
        Path(self._token_file).write_text(creds.to_json(), encoding="utf-8")
