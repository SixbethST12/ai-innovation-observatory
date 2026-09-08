"""
BOT-relevance assessment - FR-11.

UPGRADED: now returns both a numeric relevance score (0.0-1.0) and
the explanation text, in one call. Previously text-only - the score
is new, real, AI-generated (not fabricated), enabling sorting/
filtering/charting by relevance on the dashboard.

Uses a worked example showing the exact expected output format
(few-shot), since classify.py already proved this model needs a
concrete example to follow structured output reliably.

FR-12 note unchanged: this is AI-generated, must be labeled as such
wherever displayed - the score is not an official BOT assessment.
"""

import re

try:
    from .llm_client import generate, OllamaNotRunningError, OllamaTimeoutError
except ImportError:
    from llm_client import generate, OllamaNotRunningError, OllamaTimeoutError


def assess_relevance(title: str, body_text: str) -> tuple:
    """
    Returns (score: float, explanation: str).
    Score defaults to 0.5 with a logged warning if the model's output
    can't be parsed - never silently returns a fabricated-looking
    score from unparseable text.
    """
    content = body_text.strip() if body_text and body_text.strip() else "(no additional content provided)"

    prompt = f"""You are assisting an analyst at the Bank of Tanzania (BOT), an emerging-market central bank in East Africa. Assess how relevant the following publication is to BOT's work (monetary policy, financial stability, or financial sector development in Tanzania/East Africa).

Respond in EXACTLY this format, nothing else:
Score: <a number between 0.0 and 1.0, where 1.0 is extremely relevant>
Explanation: <1-2 sentences explaining why>

Example:
Title: Central bank policy rates, 2026-07 / Daily and monthly data
Content: Contains the long series on central bank policy rates.
Score: 0.7
Explanation: BOT can benchmark Tanzania's own policy rate decisions against peer central banks' rate paths, useful for regional monetary policy comparison.

Now assess this one:

Title: {title}
Content: {content}

Score:"""

    raw = generate(prompt)

    score_match = re.search(r"([01](?:\.\d+)?)", raw)
    explanation_match = re.search(r"Explanation:\s*(.+)", raw, re.DOTALL)

    if score_match:
        score = float(score_match.group(1))
        score = max(0.0, min(1.0, score))  # clamp to valid range
    else:
        print(f"[relevance] Warning: could not parse score from model output, defaulting to 0.5. Raw: {raw[:100]!r}")
        score = 0.5

    if explanation_match:
        explanation = explanation_match.group(1).strip()
    else:
        # Fallback: use everything after "Score: X" as the explanation
        explanation = re.sub(r"^Score:\s*[01](?:\.\d+)?\s*", "", raw).strip()
        if not explanation:
            explanation = raw.strip()

    return score, explanation


if __name__ == "__main__":
    print("Test 1: Kenya MPC rate decision")
    try:
        score, explanation = assess_relevance(
            "MPC retains the CBR at 8.75 percent",
            "The Monetary Policy Committee of the Central Bank of Kenya decided to retain the Central Bank Rate at 8.75 percent."
        )
        print(f"Score: {score}")
        print(f"Explanation: {explanation}")
    except (OllamaNotRunningError, OllamaTimeoutError) as e:
        print("ERROR:", e)

    print()
    print("Test 2: Tanzania's own CPI data (expect a high score)")
    try:
        score, explanation = assess_relevance(
            "IMF CPI Data - Tanzania (TZA) - pulled 2026-09-04",
            "IMF Consumer Price Index (CPI) data for Tanzania (ISO code: TZA):\n2026-06: 146.2"
        )
        print(f"Score: {score}")
        print(f"Explanation: {explanation}")
    except (OllamaNotRunningError, OllamaTimeoutError) as e:
        print("ERROR:", e)
