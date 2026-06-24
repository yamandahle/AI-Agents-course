"""
Step 2 — Ollama API Test
Runs phi3:mini via the Ollama REST API, measures response time and token count.
Saves results to results/step2_results.json.
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"
PROMPT = "What is the capital of Spain? Answer in one sentence."
RESULTS_FILE = Path(__file__).parent / "results" / "step2_results.json"


def run_inference(prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    start = time.time()
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    elapsed = time.time() - start

    response.raise_for_status()
    data = response.json()

    return {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prompt": prompt,
        "response": data.get("response", "").strip(),
        "elapsed_sec": round(elapsed, 2),
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "response_tokens": data.get("eval_count", 0),
        "tokens_per_sec": round(
            data.get("eval_count", 0) / elapsed, 2
        ) if elapsed > 0 else 0,
    }


def save_result(result: dict) -> None:
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if RESULTS_FILE.exists():
        existing = json.loads(RESULTS_FILE.read_text())
    existing.append(result)
    RESULTS_FILE.write_text(json.dumps(existing, indent=2))
    print(f"\nResult saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    print(f"Model     : {MODEL}")
    print(f"Prompt    : {PROMPT}")
    print("-" * 50)

    result = run_inference(PROMPT)

    print(f"Response  : {result['response']}")
    print("-" * 50)
    print(f"Time            : {result['elapsed_sec']} sec")
    print(f"Prompt tokens   : {result['prompt_tokens']}")
    print(f"Response tokens : {result['response_tokens']}")
    print(f"Tokens/sec      : {result['tokens_per_sec']}")

    save_result(result)
