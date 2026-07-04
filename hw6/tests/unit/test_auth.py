"""Unit tests for GmailAuth — TDD red phase. Google APIs are always mocked."""

from unittest.mock import MagicMock

import cop_thief.gmail.auth as auth_module
from cop_thief.gmail.auth import GmailAuth


def _auth(tmp_path, token_exists=False):
    token_file = tmp_path / "token.json"
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text("{}")
    if token_exists:
        token_file.write_text("{}")
    return GmailAuth(str(creds_file), str(token_file)), token_file, creds_file


def test_loads_credentials_from_file(tmp_path, monkeypatch):
    gmail_auth, token_file, _ = _auth(tmp_path, token_exists=True)
    valid_creds = MagicMock(valid=True)
    monkeypatch.setattr(
        auth_module.Credentials, "from_authorized_user_file",
        MagicMock(return_value=valid_creds),
    )

    result = gmail_auth.get_credentials()

    assert result is valid_creds


def test_refreshes_expired_token(tmp_path, monkeypatch):
    gmail_auth, token_file, _ = _auth(tmp_path, token_exists=True)
    expired_creds = MagicMock(valid=False, expired=True, refresh_token="rt")
    expired_creds.to_json.return_value = '{"refreshed": true}'
    monkeypatch.setattr(
        auth_module.Credentials, "from_authorized_user_file",
        MagicMock(return_value=expired_creds),
    )
    monkeypatch.setattr(auth_module, "Request", MagicMock())

    result = gmail_auth.get_credentials()

    expired_creds.refresh.assert_called_once()
    assert result is expired_creds


def test_saves_refreshed_token(tmp_path, monkeypatch):
    gmail_auth, token_file, _ = _auth(tmp_path, token_exists=True)
    expired_creds = MagicMock(valid=False, expired=True, refresh_token="rt")
    expired_creds.to_json.return_value = '{"refreshed": true}'
    monkeypatch.setattr(
        auth_module.Credentials, "from_authorized_user_file",
        MagicMock(return_value=expired_creds),
    )
    monkeypatch.setattr(auth_module, "Request", MagicMock())

    gmail_auth.get_credentials()

    assert token_file.read_text() == '{"refreshed": true}'


def test_missing_credentials_raises_error(tmp_path):
    gmail_auth, _, creds_file = _auth(tmp_path, token_exists=False)
    creds_file.unlink()

    try:
        gmail_auth.get_credentials()
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_first_run_launches_browser_flow(tmp_path, monkeypatch):
    gmail_auth, token_file, _ = _auth(tmp_path, token_exists=False)
    new_creds = MagicMock()
    new_creds.to_json.return_value = '{"new": true}'
    mock_flow = MagicMock()
    mock_flow.run_local_server.return_value = new_creds
    monkeypatch.setattr(
        auth_module.InstalledAppFlow, "from_client_secrets_file",
        MagicMock(return_value=mock_flow),
    )

    result = gmail_auth.get_credentials()

    mock_flow.run_local_server.assert_called_once_with(port=0)
    assert result is new_creds
    assert token_file.read_text() == '{"new": true}'
