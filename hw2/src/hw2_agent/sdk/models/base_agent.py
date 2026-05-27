import abc
from pathlib import Path
from ...services.fifo_logger import setup_fifo_logger

logger = setup_fifo_logger()

class BaseAgent(abc.ABC):
    """
    Abstract parent class for all agents in the debate system.
    """
    def __init__(self, name: str, persona_path: str):
        self.name = name
        self.persona_path = Path(persona_path)
        self.logger = logger
        self.persona = self._load_persona()
        self.token_usage = {"prompt": 0, "completion": 0}

    def _load_persona(self) -> str:
        """Loads the project-scoped markdown persona from disk."""
        if not self.persona_path.exists():
            self.logger.warning(f"Persona file {self.persona_path} not found. Using empty persona.")
            return ""
        return self.persona_path.read_text(encoding="utf-8")

    def load_recovery_context(self) -> str:
        """Reads the brief checkpoint for agent re-initialization."""
        from ...services.recovery_logger import load_recovery_checkpoint
        return load_recovery_checkpoint()

    @abc.abstractmethod
    def run_turn(self, context: list[dict]) -> str:
        """Executes a single turn for the agent."""
        pass

    def get_token_stats(self) -> dict:
        """Returns the cumulative token usage for this agent."""
        return self.token_usage
