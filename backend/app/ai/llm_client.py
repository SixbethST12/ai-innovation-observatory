"""
LLM client wrapper - the single place all AI layer code calls Ollama through.

Centralizes: reading which model to use from .env, calling Ollama's
API, and handling the case where Ollama isn't running (a real
operational risk - Ollama must be manually started with `ollama serve`
in this Codespace, since there's no systemd to auto-start it).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")


class OllamaNotRunningError(Exception):
    """Raised when Ollama's API can't be reached at all."""
    pass


def generate(prompt: str, timeout: int = 60) -> str:
    """
    Sends a prompt to the local Ollama model, returns the generated text.
    Raises OllamaNotRunningError with a clear message if Ollama isn't
    reachable, so calling code can handle that case distinctly from a
    normal generation failure.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise OllamaNotRunningError(
            "Could not reach Ollama at http://localhost:11434 - "
            "is it running? Start it with: ollama serve > /tmp/ollama.log 2>&1 &"
        )


if __name__ == "__main__":
    # Self-test: real call to Ollama, using the real project setup
    print(f"Using model: {MODEL_NAME}")
    try:
        result = generate("Summarize in one sentence: Tanzania's central bank held interest rates steady this quarter.")
        print("Generated:", result)
    except OllamaNotRunningError as e:
        print("ERROR:", e)
