"""Unit tests for GmailSender — TDD red phase. Gmail API is always mocked."""

import base64
import json
from unittest.mock import MagicMock

import pytest

import cop_thief.gmail.sender as sender_module
from cop_thief.api_gatekeeper import ApiGatekeeper
from cop_thief.gmail.sender import GmailSender

CONFIG = {
    "gmail": {"recipient": "rmisegal+uoh26b@gmail.com"},
    "reporting": {"group_name": "Team-Alpha"},
}
LLM_CONFIG = {"base_url": "http://localhost:11434", "timeout_seconds": 30}
RATE_LIMITS = {
    "ollama": {"calls_per_minute": 30, "max_retries": 3},
    "gmail": {"calls_per_minute": 10, "max_retries": 3},
}
REPORT = {"group_name": "Team-Alpha", "totals": {"cop": 20, "thief": 5}}


def _decoded_body(mock_service) -> str:
    call_kwargs = mock_service.users().messages().send.call_args.kwargs
    raw = call_kwargs["body"]["raw"]
    return base64.urlsafe_b64decode(raw.encode()).decode()


def _make_sender(tmp_path, mock_service):
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value = MagicMock()
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=MagicMock())
    log_file = str(tmp_path / "gmail_log.json")
    sender = GmailSender(mock_auth, gatekeeper, log_file=log_file)
    return sender, mock_auth


def _mock_service(send_result=None):
    service = MagicMock()
    service.users().messages().send().execute.return_value = send_result or {"id": "m1"}
    return service


async def test_email_sent_to_correct_recipient(tmp_path, monkeypatch):
    service = _mock_service()
    monkeypatch.setattr(sender_module, "build", MagicMock(return_value=service))
    sender, _ = _make_sender(tmp_path, service)

    await sender.send(REPORT, CONFIG)

    body_text = _decoded_body(service)
    assert "rmisegal+uoh26b@gmail.com" in body_text


async def test_email_body_is_json_only(tmp_path, monkeypatch):
    service = _mock_service()
    monkeypatch.setattr(sender_module, "build", MagicMock(return_value=service))
    sender, _ = _make_sender(tmp_path, service)

    await sender.send(REPORT, CONFIG)

    body_text = _decoded_body(service)
    # The MIME envelope has headers; the payload after them must be pure JSON.
    payload = body_text.split("\n\n", 1)[1]
    parsed = json.loads(payload)
    assert parsed == REPORT


async def test_email_sent_exactly_once(tmp_path, monkeypatch):
    service = _mock_service()
    monkeypatch.setattr(sender_module, "build", MagicMock(return_value=service))
    sender, _ = _make_sender(tmp_path, service)

    await sender.send(REPORT, CONFIG)

    assert service.users().messages().send().execute.call_count == 1


async def test_retry_on_api_failure(tmp_path, monkeypatch):
    calls = {"n": 0}

    def flaky_build(*args, **kwargs):
        calls["n"] += 1
        service = MagicMock()
        if calls["n"] == 1:
            service.users().messages().send().execute.side_effect = RuntimeError("boom")
        else:
            service.users().messages().send().execute.return_value = {"id": "m1"}
        return service

    monkeypatch.setattr(sender_module, "build", flaky_build)
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value = MagicMock()
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=MagicMock())
    log_file = str(tmp_path / "gmail_log.json")
    sender = GmailSender(mock_auth, gatekeeper, log_file=log_file)

    await sender.send(REPORT, CONFIG)

    assert calls["n"] == 2


async def test_send_result_logged(tmp_path, monkeypatch):
    service = _mock_service()
    monkeypatch.setattr(sender_module, "build", MagicMock(return_value=service))
    log_file = tmp_path / "gmail_log.json"
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value = MagicMock()
    gatekeeper = ApiGatekeeper(LLM_CONFIG, RATE_LIMITS, client=MagicMock())
    sender = GmailSender(mock_auth, gatekeeper, log_file=str(log_file))

    await sender.send(REPORT, CONFIG)

    logged = json.loads(log_file.read_text())
    assert logged["status"] == "ok"
    assert logged["recipient"] == "rmisegal+uoh26b@gmail.com"


async def test_send_logs_failure_and_reraises(tmp_path, monkeypatch):
    def always_fails(*args, **kwargs):
        service = MagicMock()
        service.users().messages().send().execute.side_effect = RuntimeError("boom")
        return service

    monkeypatch.setattr(sender_module, "build", always_fails)
    log_file = tmp_path / "gmail_log.json"
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value = MagicMock()
    limits = {**RATE_LIMITS, "gmail": {"calls_per_minute": 10, "max_retries": 2}}
    gatekeeper = ApiGatekeeper(LLM_CONFIG, limits, client=MagicMock())
    sender = GmailSender(mock_auth, gatekeeper, log_file=str(log_file))

    with pytest.raises(Exception):
        await sender.send(REPORT, CONFIG)

    logged = json.loads(log_file.read_text())
    assert logged["status"] == "failed"
