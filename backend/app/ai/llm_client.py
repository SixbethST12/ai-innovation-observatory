"""
LLM client wrapper - the single place all AI layer code calls Ollama through.

Centralizes: reading which model to use from .env, calling Ollama's
API, and handling failures distinctly so callers can react correctly.

BUG FOUND AND FIXED (real incident): the original version only caught
ConnectionError (Ollama not running at all). A single generation call
exceeded the timeout, raised an UNCAUGHT ReadTimeout exception, which
crashed the entire background scheduler process - killing all future
scheduled cycles, not just that one record. Confirmed via
/tmp/scheduler.log traceback. Fixed by:
  1. Catching timeouts as a distinct, specific error type
     (OllamaTimeoutError), separate from "Ollama isn't running"
     (OllamaNotRunningError) - callers need to react differently to
     each (stop everything vs skip one record and continue).
  2. Raising the default timeout from 60s to 120s, since real
     generations were already observed taking up to 47.8s in a batch
     of 30 - 60s left too little margin.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")


class OllamaNotRunningError(Exception):
    """Ollama's API can't be reached at all - stop, don't retry immediately."""
    pass


class OllamaTimeoutError(Exception):
    """Ollama is running but this specific call took too long - safe to skip and continue."""
    pass


def generate(prompt: str, timeout: int = 120) -> str:
    """
    Sends a prompt to the local Ollama model, returns the generated text.
    Raises OllamaNotRunningError if Ollama isn't reachable at all, or
    OllamaTimeoutError if this specific call timed out - these are
    handled differently by callers (processor.py).
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
    except requests.exceptions.Timeout:
        raise OllamaTimeoutError(
            f"Ollama call exceeded {timeout}s timeout - this record will be retried next cycle"
        )


if __name__ == "__main__":
    print(f"Using model: {MODEL_NAME}")
    try:
        result = generate("Summarize in one sentence: Tanzania's central bank held interest rates steady this quarter.")
        print("Generated:", result)
    except OllamaNotRunningError as e:
        print("ERROR (not running):", e)
    except OllamaTimeoutError as e:
        print("ERROR (timeout):", e)
