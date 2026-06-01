"""Unit tests for DebateSDK — TDD Red phase written before implementation."""

from __future__ import annotations

import pytest

from debate.sdk.sdk import DebateSDK, DebateSession, SessionNotFoundError


def _make_sdk() -> DebateSDK:
    return DebateSDK()


# ---------------------------------------------------------------------------
# 1. start_debate returns a valid session
# ---------------------------------------------------------------------------
class TestStartDebate:
    def test_returns_debate_session(self) -> None:
        """start_debate must return a DebateSession instance."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Remote vs Office", config_path="config/setup.json")
        assert isinstance(session, DebateSession)

    def test_session_has_non_empty_id(self) -> None:
        """Returned session must have a non-empty session_id string."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Remote vs Office", config_path="config/setup.json")
        assert isinstance(session.session_id, str)
        assert len(session.session_id) > 0

    def test_session_topic_matches_argument(self) -> None:
        """Session topic must equal the topic passed to start_debate."""
        sdk = _make_sdk()
        topic = "Is remote work better than office work?"
        session = sdk.start_debate(topic=topic, config_path="config/setup.json")
        assert session.topic == topic

    def test_each_session_has_unique_id(self) -> None:
        """Two consecutive start_debate calls must produce different session IDs."""
        sdk = _make_sdk()
        s1 = sdk.start_debate(topic="Topic A", config_path="config/setup.json")
        s2 = sdk.start_debate(topic="Topic B", config_path="config/setup.json")
        assert s1.session_id != s2.session_id

    def test_new_session_status_is_running(self) -> None:
        """A freshly started session must have status 'running'."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Topic", config_path="config/setup.json")
        assert session.status == "running"


# ---------------------------------------------------------------------------
# 2. get_status returns correct fields
# ---------------------------------------------------------------------------
class TestGetStatus:
    def test_get_status_returns_dict_with_required_fields(self) -> None:
        """get_status must return a dict with session_id, status, and topic."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Remote work", config_path="config/setup.json")
        status = sdk.get_status(session.session_id)
        assert {"session_id", "status", "topic"}.issubset(status.keys())

    def test_get_status_matches_session_state(self) -> None:
        """Status values must match the underlying session's attributes."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Office debate", config_path="config/setup.json")
        status = sdk.get_status(session.session_id)
        assert status["session_id"] == session.session_id
        assert status["status"] == "running"
        assert status["topic"] == "Office debate"


# ---------------------------------------------------------------------------
# 3. get_transcript returns a list (empty initially)
# ---------------------------------------------------------------------------
class TestGetTranscript:
    def test_transcript_is_empty_on_new_session(self) -> None:
        """A new session must have an empty transcript."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Topic", config_path="config/setup.json")
        transcript = sdk.get_transcript(session.session_id)
        assert transcript == []

    def test_get_transcript_returns_copy(self) -> None:
        """Mutating the returned transcript must not affect internal session state."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Topic", config_path="config/setup.json")
        t = sdk.get_transcript(session.session_id)
        t.append("rogue entry")  # type: ignore[arg-type]
        assert sdk.get_transcript(session.session_id) == []


# ---------------------------------------------------------------------------
# 4. get_cost_report returns a dict (empty initially)
# ---------------------------------------------------------------------------
class TestGetCostReport:
    def test_cost_report_is_empty_on_new_session(self) -> None:
        """A new session must have an empty cost report dict."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Topic", config_path="config/setup.json")
        report = sdk.get_cost_report(session.session_id)
        assert report == {}

    def test_get_cost_report_returns_copy(self) -> None:
        """Mutating the returned report must not affect internal session state."""
        sdk = _make_sdk()
        session = sdk.start_debate(topic="Topic", config_path="config/setup.json")
        report = sdk.get_cost_report(session.session_id)
        report["rogue"] = True
        assert sdk.get_cost_report(session.session_id) == {}


# ---------------------------------------------------------------------------
# 5. Unknown session_id raises SessionNotFoundError
# ---------------------------------------------------------------------------
class TestUnknownSession:
    def test_get_status_raises_for_unknown_id(self) -> None:
        sdk = _make_sdk()
        with pytest.raises(SessionNotFoundError):
            sdk.get_status("nonexistent-id")

    def test_get_transcript_raises_for_unknown_id(self) -> None:
        sdk = _make_sdk()
        with pytest.raises(SessionNotFoundError):
            sdk.get_transcript("nonexistent-id")

    def test_get_cost_report_raises_for_unknown_id(self) -> None:
        sdk = _make_sdk()
        with pytest.raises(SessionNotFoundError):
            sdk.get_cost_report("nonexistent-id")
