import os
from typing import Any
import anthropic
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self._setup_client()

    def _setup_client(self):
        api_key = os.getenv("ACTIVE_API_KEY")
        if not api_key:
            raise ValueError("ACTIVE_API_KEY not found in environment")

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate_response(self, system_prompt: str, messages: list[dict]) -> tuple[str, dict]:
        if os.getenv("MOCK_LLM") == "true":
            # Determine if we need to return JSON
            last_message = messages[-1]["message"] if messages else ""
            if "round_judgment" in system_prompt or "JUDGE_ROUND_PROMPT" in last_message or "judged" in system_prompt.lower():
                return '{"round_judgment": {"round_winner": "Proponent", "quality_score": 8, "justification": "Better logic."}}', {"prompt": 0, "completion": 0}
            if "FINAL_VERDICT_PROMPT" in system_prompt or "verdict" in system_prompt.lower():
                return '{"verdict": {"final_winner": "Proponent", "tie_breaker_justification": "N/A", "detailed_report": "The Proponent argued consistently about the benefits of AI in arts."}}', {"prompt": 0, "completion": 0}
            
            speaker = "AI"
            if "Proponent" in system_prompt: speaker = "Proponent"
            elif "Opponent" in system_prompt: speaker = "Opponent"
            elif "Judge" in system_prompt: speaker = "Judge"
            return f"Simulated response for {speaker}.", {"prompt": 0, "completion": 0}

        if self.provider == "anthropic":
            # Convert messages to Anthropic format
            anthropic_messages = []
            for m in messages:
                role = "user" if m["speaker"] in ["Proponent", "Opponent", "Judge"] else "assistant"
                # Actually, in this system, the "assistant" is the one we are calling.
                # The context contains history of other speakers.
                # For Anthropic, the history should be alternating.
                # This might be tricky if we have Proponent and Opponent history.
                # Usually we can treat all previous turns as user messages for the current agent.
                anthropic_messages.append({"role": "user", "content": f"{m['speaker']}: {m['message']}"})
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=system_prompt,
                messages=anthropic_messages
            )
            text = response.content[0].text
            usage = {
                "prompt": response.usage.input_tokens,
                "completion": response.usage.output_tokens
            }
            return text, usage
        
        elif self.provider == "gemini":
            # Gemini format
            prompt = f"System: {system_prompt}\n\n"
            for m in messages:
                prompt += f"{m['speaker']}: {m['message']}\n"
            
            response = self.model.generate_content(prompt)
            # Gemini token usage is a bit different to get
            usage = {
                "prompt": response.usage_metadata.prompt_token_count,
                "completion": response.usage_metadata.candidates_token_count
            }
            return response.text, usage
        
        return "", {"prompt": 0, "completion": 0}
