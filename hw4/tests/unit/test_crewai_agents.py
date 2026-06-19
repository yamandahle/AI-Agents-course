"""Unit tests for crewai_agents/agents.py."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from hw4.shared.provider import ProviderConfig

_PROVIDER = ProviderConfig(
    name="openai", api_key="test-key-abc", model="gpt-4o-mini", rate_limit_key="openai"
)


def _build(provider=_PROVIDER):
    from hw4.crewai_agents.agents import build_agents

    with (
        patch("hw4.crewai_agents.agents.LLM") as mock_llm,
        patch("hw4.crewai_agents.agents.Agent") as mock_agent,
    ):
        mock_agent.return_value = MagicMock()
        agents = build_agents(provider=provider)
    return agents, mock_llm, mock_agent


def test_build_agents_returns_all_four_keys() -> None:
    agents, _, _ = _build()
    assert set(agents.keys()) == {
        "graph_navigator",
        "architect_detective",
        "fix_strategist",
        "quality_gate",
    }


def test_build_agents_uses_provider_model() -> None:
    _, mock_llm, _ = _build()
    mock_llm.assert_called_once_with(
        model="gpt-4o-mini", api_key="test-key-abc", temperature=0.2
    )


def test_build_agents_creates_four_agent_instances() -> None:
    _, _, mock_agent = _build()
    assert mock_agent.call_count == 4


def test_build_agents_defaults_to_load_provider() -> None:
    from hw4.crewai_agents.agents import build_agents

    fake_provider = ProviderConfig(
        name="gemini", api_key="gem-key", model="gemini/flash", rate_limit_key="gemini"
    )
    with (
        patch("hw4.crewai_agents.agents.load_provider", return_value=fake_provider),
        patch("hw4.crewai_agents.agents.LLM") as mock_llm,
        patch("hw4.crewai_agents.agents.Agent", return_value=MagicMock()),
    ):
        build_agents()  # no provider arg → calls load_provider()
    mock_llm.assert_called_once_with(
        model="gemini/flash", api_key="gem-key", temperature=0.2
    )
