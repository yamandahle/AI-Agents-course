from .base_agent import BaseAgent
from ..client import LLMClient
from ...shared.constants import JUDGE_ROUND_PROMPT, FINAL_VERDICT_PROMPT
import json

class JudgeAgent(BaseAgent):
    def __init__(self, name: str, persona_path: str, provider: str = "anthropic"):
        super().__init__(name, persona_path)
        self.client = LLMClient(provider=provider)

    def run_turn(self, context: list[dict]) -> str:
        """
        Executes a judge turn to relay messages or provide interventions.
        """
        system_prompt = self.persona + "\n\nYou are the relay and moderator. Ensure the debate stays on track."
        response_text, usage = self.client.generate_response(system_prompt, context)
        
        self.token_usage["prompt"] += usage["prompt"]
        self.token_usage["completion"] += usage["completion"]
        
        return response_text

    def judge_round(self, topic: str, speech_type: str, proponent_msg: str, opponent_msg: str) -> dict:
        """
        Judges a single round (exchange) and returns a JSON judgment.
        """
        system_prompt = self.persona + "\n\nYou must judge this round strictly."
        prompt = JUDGE_ROUND_PROMPT.format(
            topic=topic,
            speech_type=speech_type,
            proponent_speech_json=json.dumps({"speaker": "Proponent", "message": proponent_msg}),
            opponent_speech_json=json.dumps({"speaker": "Opponent", "message": opponent_msg})
        )
        
        # We use generate_response but the prompt is the 'user' part or we can mix it.
        # For simplicity, I'll pass the prompt as the only message in context for this call
        # but keep the system persona.
        
        response_text, usage = self.client.generate_response(system_prompt, [{"speaker": "System", "message": prompt}])
        
        self.token_usage["prompt"] += usage["prompt"]
        self.token_usage["completion"] += usage["completion"]
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(response_text[start:end])
        except Exception as e:
            self.logger.error(f"Failed to parse round judgment: {str(e)}")
            
        return {"round_judgment": {"error": "Failed to parse"}}

    def evaluate_winner(self, context: list[dict]) -> dict:
        """
        Final evaluation to determine a winner. No ties allowed.
        """
        system_prompt = self.persona + "\n\n" + FINAL_VERDICT_PROMPT
        
        response_text, usage = self.client.generate_response(system_prompt, context)
        
        self.token_usage["prompt"] += usage["prompt"]
        self.token_usage["completion"] += usage["completion"]
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(response_text[start:end])
        except Exception as e:
            self.logger.error(f"Failed to parse final verdict: {str(e)}")
            
        return {"verdict": {"final_winner": "Unknown", "tie_breaker_justification": response_text}}
