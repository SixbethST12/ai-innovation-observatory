"""
BOT-relevance assessment - FR-11.

Pure function: takes a title + body text, returns a short explanation
of why this publication matters specifically to Bank of Tanzania.

Uses a worked example in the prompt (few-shot), consistent with
classify.py's approach.

FIX: the model was echoing "Relevance:" back at the start of its own
output (doubled up with the label already in the prompt) - stripped
in code below, since this is a deterministic formatting issue, not
worth solving via more prompt engineering.

KNOWN LIMITATION (documented, not fixed): the model occasionally
drops spaces between words (e.g. "monetarypolicy") - a tokenization
quirk of this small model, consistent with issues seen in
summarize.py. Not reliably fixable via prompting.

IMPORTANT - FR-12 note: this returns AI-generated text only. FR-12
requires this to be clearly LABELED as AI-generated wherever it's
displayed - that labeling must happen at the dashboard/display layer
(not yet built), not enforced from this file.
"""

try:
    from .llm_client import generate, OllamaNotRunningError
except ImportError:
    from llm_client import generate, OllamaNotRunningError


def assess_relevance(title: str, body_text: str) -> str:
    content = body_text.strip() if body_text and body_text.strip() else "(no additional content provided)"

    prompt = f"""You are assisting an analyst at the Bank of Tanzania (BOT), an emerging-market central bank in East Africa. Explain in 1-2 sentences why the following publication is specifically relevant to BOT's work (monetary policy, financial stability, or financial sector development in Tanzania/East Africa) - not why it matters to central banks in general.

Example:
Title: Central bank policy rates, 2026-07 / Daily and monthly data
Content: Contains the long series on central bank policy rates.
Relevance: BOT can benchmark Tanzania's own policy rate decisions against peer central banks' rate paths, useful for regional monetary policy comparison.

Now assess this one:

Title: {title}
Content: {content}

Relevance:"""

    result = generate(prompt)

    # Strip a leading "Relevance:" if the model echoed the label back
    if result.lower().startswith("relevance:"):
        result = result[len("relevance:"):].strip()

    return result


if __name__ == "__main__":
    print("Test 1: Kenya MPC rate decision")
    test_title1 = "MPC retains the CBR at 8.75 percent"
    test_body1 = "The Monetary Policy Committee of the Central Bank of Kenya decided to retain the Central Bank Rate at 8.75 percent, citing stable inflation expectations."
    try:
        result1 = assess_relevance(test_title1, test_body1)
        print("Relevance:", result1)
    except OllamaNotRunningError as e:
        print("ERROR:", e)

    print()
    print("Test 2: Tanzania's own IMF CPI data")
    test_title2 = "IMF CPI Data - TZA - pulled 2026-08-31"
    test_body2 = "IMF CPI (Consumer Price Index) for TZA:\n2026-01: 142.3\n2026-06: 146.2"
    try:
        result2 = assess_relevance(test_title2, test_body2)
        print("Relevance:", result2)
    except OllamaNotRunningError as e:
        print("ERROR:", e)
