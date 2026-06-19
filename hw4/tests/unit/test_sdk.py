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


def test_sdk_verify_delegates_to_verify_service() -> None:
    from hw4.services.verify_service import VerifyResult

    sdk = HW4SDK("config")
    fake = VerifyResult({}, True, 90.0, True, "reports/verification.md")
    with patch("hw4.sdk.sdk.VerifyService") as mock_verify:
        mock_verify.return_value.run.return_value = fake
        result = sdk.verify()
    assert result.coverage_percent == 90.0


def test_sdk_apply_fix_delegates() -> None:
    from hw4.services.fix_applier import FixResult

    sdk = HW4SDK("config")
    fake = FixResult("fix/test", "results/fix_diff.patch", "main.py", True)
    with patch("hw4.sdk.sdk.FixApplierService") as mock_applier:
        mock_applier.return_value.apply_from_file.return_value = fake
        result = sdk.apply_fix()
    assert result.branch == "fix/test"
