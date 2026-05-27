import json
import os
from hw2_agent.services.analytics import update_analytics, ANALYTICS_PATH

def test_update_analytics(tmp_path, monkeypatch):
    test_analytics_path = tmp_path / "win_loss_matrix.json"
    monkeypatch.setattr("hw2_agent.services.analytics.ANALYTICS_PATH", test_analytics_path)
    # Mock load_config to return empty dict so it falls back to ANALYTICS_PATH
    monkeypatch.setattr("hw2_agent.services.analytics.load_config", lambda: {})
    
    # Test first win
    data = update_analytics("Proponent")
    assert data["total_debates_run"] == 1
    assert data["proponent_wins"] == 1
    assert data["opponent_wins"] == 0
    
    # Test second win
    data = update_analytics("Opponent")
    assert data["total_debates_run"] == 2
    assert data["proponent_wins"] == 1
    assert data["opponent_wins"] == 1
    
    # Check file content
    with open(test_analytics_path, "r") as f:
        file_data = json.load(f)
    assert file_data == data

def test_display_full_analytics_report(tmp_path, monkeypatch, capsys):
    test_analytics_path = tmp_path / "win_loss_matrix.json"
    monkeypatch.setattr("hw2_agent.services.analytics.ANALYTICS_PATH", test_analytics_path)
    monkeypatch.setattr("hw2_agent.services.analytics.load_config", lambda: {})
    
    from hw2_agent.services.analytics import display_full_analytics_report
    
    # Test with no data
    display_full_analytics_report()
    captured = capsys.readouterr()
    assert "No analytics data recorded yet" in captured.out
    
    # Add some data
    update_analytics("Proponent", points={"Proponent": 2, "Opponent": 1}, verdict={"justification": "Clear arguments"})
    
    display_full_analytics_report()
    captured = capsys.readouterr()
    assert "MULTI-AGENT DEBATE PLATFORM" in captured.out
    assert "Proponent Win Record          : 1" in captured.out
    assert "Clear arguments" in captured.out
