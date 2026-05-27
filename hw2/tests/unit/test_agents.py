import pytest
from pathlib import Path
from hw2_agent.sdk.models.base_agent import BaseAgent

class MockAgent(BaseAgent):
    def run_turn(self, context: list[dict]) -> str:
        return "Mock response"

def test_persona_loading(tmp_path):
    persona_file = tmp_path / "persona.md"
    persona_file.write_text("# Persona content")
    
    agent = MockAgent("TestAgent", str(persona_file))
    assert agent.persona == "# Persona content"

def test_missing_persona(caplog):
    agent = MockAgent("TestAgent", "non_existent.md")
    assert agent.persona == ""
    assert "Persona file non_existent.md not found" in caplog.text
