from .base_agent import BaseAgent
from ..client import LLMClient
from ..search import web_search

class DebaterAgent(BaseAgent):
    def __init__(self, name: str, persona_path: str, provider: str = "anthropic"):
        super().__init__(name, persona_path)
        self.client = LLMClient(provider=provider)

    def run_turn(self, context: list[dict], search_query: str = None, speech_instructions: dict = None) -> tuple[str, list[str]]:
        """
        Executes a debater turn. If a search query is provided, it grounds the argument with live data.
        """
        search_results = ""
        queries = []
        if search_query:
            self.logger.info(f"{self.name} is searching for: {search_query}")
            search_results = web_search(search_query)
            queries.append(search_query)

        system_prompt = self.persona
        
        if not context:
            recovery_context = self.load_recovery_context()
            if recovery_context:
                system_prompt += f"\n\n### RECOVERY CONTEXT:\n{recovery_context}\n"

        if search_results:
            system_prompt += f"\n\nSearch Results for grounding:\n{search_results}"
            
        if speech_instructions:
            system_prompt += f"\n\n### CURRENT TURN INSTRUCTIONS ({speech_instructions.get('speech_type')}):\n"
            for key, val in speech_instructions.get('required_structure', {}).items():
                system_prompt += f"**{key}**: {val}\n"

        response_text, usage = self.client.generate_response(system_prompt, context)
        
        self.token_usage["prompt"] += usage["prompt"]
        self.token_usage["completion"] += usage["completion"]
        
        return response_text, queries
