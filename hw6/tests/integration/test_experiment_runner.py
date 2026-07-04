"""Integration tests for the experiment runner CLI."""

from unittest.mock import patch

from cop_thief.experiments.runner import build_summary_and_graphs


@patch("cop_thief.experiments.runner.generate_all")
@patch("cop_thief.experiments.runner.write_summary_csv")
@patch("cop_thief.experiments.runner._build_metrics_for_case")
def test_graphs_only_builds_from_existing(
    mock_metrics, mock_csv, mock_graphs, tmp_path,
):
    mock_metrics.side_effect = [
        {"case_name": "exp1_full_5x5", "cop_wins": 4},
        None,
        None,
    ]
    mock_csv.return_value = tmp_path / "summary.csv"

    with patch("cop_thief.experiments.runner.PROJECT_ROOT", tmp_path):
        tmp_path.mkdir(exist_ok=True)
        build_summary_and_graphs()

    mock_csv.assert_called_once()
    mock_graphs.assert_called_once()
