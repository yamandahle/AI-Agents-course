from __future__ import annotations

from unittest.mock import patch

from hw4.sdk.sdk import HW4SDK


def test_sdk_run_agents_delegates_to_crew_runner() -> None:
    sdk = HW4SDK("config")
    fake_payload = {"bugs": [{"bug_type": "HUB"}], "proposals": [{}]}
    with patch("hw4.sdk.sdk.CrewRunnerService") as mock_runner:
        mock_runner.return_value.run.return_value = fake_payload
        result = sdk.run_agents()
    assert result == fake_payload
    mock_runner.assert_called_once()
    assert sdk.graph_builder is not None
