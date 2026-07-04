"""Sends the JSON-only game report email via the Gmail API."""

import base64
import json
import logging
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from googleapiclient.discovery import build

from cop_thief.api_gatekeeper import ApiGatekeeper
from cop_thief.gmail.auth import GmailAuth

logger = logging.getLogger(__name__)


class GmailSender:
    """Sends one JSON-only report email via Gmail, through ApiGatekeeper."""

    def __init__(
        self, auth: GmailAuth, gatekeeper: ApiGatekeeper,
        log_file: str = "results/gmail_log.json",
    ):
        self._auth = auth
        self._gatekeeper = gatekeeper
        self._log_file = log_file

    async def send(self, report: dict, config: dict) -> None:
        """Send report as the email body (JSON only), retried via ApiGatekeeper."""
        recipient = config["gmail"]["recipient"]
        group_name = config["reporting"]["group_name"]
        body = json.dumps(report, indent=2)
        try:
            await self._gatekeeper.call_sync(
                "gmail", lambda: self._send_via_api(recipient, group_name, body)
            )
            self._log_result(recipient, "ok")
        except Exception:
            self._log_result(recipient, "failed")
            raise

    def _send_via_api(self, recipient: str, group_name: str, body: str) -> dict:
        """Build and send the email via the Gmail API (blocking, google client)."""
        creds = self._auth.get_credentials()
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message["To"] = recipient
        message["Subject"] = f"Game Report — {group_name}"
        message.set_content(body)
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

    def _log_result(self, recipient: str, status: str) -> None:
        """Record the send attempt's outcome to log_file."""
        entry = {
            "sent_at": datetime.now().isoformat(),
            "status": status,
            "recipient": recipient,
        }
        Path(self._log_file).write_text(json.dumps(entry, indent=2))
        logger.info("Gmail send %s for %s", status, recipient)
