"""
Summarization - FR-5.

Pure function: takes a title + body text, returns a short summary.
Deliberately does NOT touch the database directly - that's
processor.py's job later. Keeping this function pure (text in, text
out) means it can be tested and reused without any DB setup.
"""

try:
    from .llm_client import generate, OllamaNotRunningError
except ImportError:
    from llm_client import generate, OllamaNotRunningError


def summarize(title: str, body_text: str) -> str:
    """
    Generates a 2-3 sentence summary of a publication. Falls back to
    just the title if body_text is empty (some real records, like
    BIS statistical releases, have thin body text).
    """
    content = body_text.strip() if body_text and body_text.strip() else "(no additional content provided)"

    prompt = f"""Summarize the following central banking or financial publication in 2-3 clear sentences. Focus on the key facts only, no commentary.

Title: {title}
Content: {content}

Summary:"""

    return generate(prompt)


if __name__ == "__main__":
    # Self-test using a real-shaped example, similar to actual stored records
    test_title = "IMF CPI Data - TZA - pulled 2026-08-31"
    test_body = """IMF CPI (Consumer Price Index) for TZA:
2026-01: 142.3
2026-02: 143.1
2026-03: 144.0
2026-04: 144.8
2026-05: 145.6
2026-06: 146.2"""

    print("Generating summary for test record...")
    try:
        result = summarize(test_title, test_body)
        print("\nSummary:", result)
    except OllamaNotRunningError as e:
        print("ERROR:", e)
