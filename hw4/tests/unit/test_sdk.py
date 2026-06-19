from __future__ import annotations

from unittest.mock import patch

from hw4.sdk.sdk import HW4SDK


def test_sdk_run_agents_delegates_to_crew_runner() -> None:
    sdk = HW4SDK("config")
    fake_payload = {"bugs": [{"bug_type": "HUB"}], "proposals": [{}]}
    with patch("hw4.sdk.sdk.CrewRunnerV2") as mock_runner:
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
    from hw4.services.generic_fix_applier import FixResult

    sdk = HW4SDK("config")
    fake = FixResult("fix/test", "results/fix_diff.patch", "main.py", True)
    with patch("hw4.sdk.sdk.GenericFixApplier") as mock_applier:
        mock_applier.return_value.apply_from_proposal.return_value = fake
        result = sdk.apply_fix()
    assert result.branch == "fix/test"


def test_sdk_run_grphify_calls_graph_builder(tmp_path) -> None:
    sdk = HW4SDK("config")
    with (
        patch.object(sdk.graph_builder, "package_dir", return_value=tmp_path) as mock_pkg,
        patch.object(sdk.graph_builder, "run_grphify", return_value=tmp_path) as mock_run,
        patch.object(sdk.graph_builder, "sync_deliverables") as mock_sync,
    ):
        sdk.run_grphify(project_root=str(tmp_path))

    mock_pkg.assert_called_once()
    mock_run.assert_called_once()
    mock_sync.assert_called_once()


def test_sdk_detect_bugs_returns_list() -> None:
    from unittest.mock import MagicMock

    sdk = HW4SDK("config")
    fake_metrics = MagicMock()
    fake_metrics.node_count = 5
    fake_metrics.edge_count = 10
    fake_metrics.community_count = 2
    fake_metrics.top_hubs = []
    fake_metrics.bridge_count = 3

    with (
        patch.object(sdk.graph_builder, "load_graph", return_value=MagicMock()),
        patch.object(sdk.graph_builder, "compute_metrics", return_value=fake_metrics),
        patch("hw4.sdk.sdk.BugDetectorService") as mock_detector,
    ):
        mock_detector.return_value.detect.return_value = []
        result = sdk.detect_bugs()

    assert result == []


def test_sdk_detect_bugs_maps_to_dict() -> None:
    from unittest.mock import MagicMock

    sdk = HW4SDK("config")
    fake_metrics = MagicMock()
    fake_metrics.node_count = 3
    fake_metrics.edge_count = 5
    fake_metrics.community_count = 1
    fake_metrics.top_hubs = []
    fake_metrics.bridge_count = 0

    fake_bug = MagicMock()
    fake_bug.to_dict.return_value = {"bug_type": "HUB", "node_name": "x"}

    with (
        patch.object(sdk.graph_builder, "load_graph", return_value=MagicMock()),
        patch.object(sdk.graph_builder, "compute_metrics", return_value=fake_metrics),
        patch("hw4.sdk.sdk.BugDetectorService") as mock_detector,
    ):
        mock_detector.return_value.detect.return_value = [fake_bug]
        result = sdk.detect_bugs()

    assert len(result) == 1
    assert result[0]["bug_type"] == "HUB"
