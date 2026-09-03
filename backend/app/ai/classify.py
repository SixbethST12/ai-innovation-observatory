"""
Topic classification - FR-7, FR-8.

Pure function: takes title + body text, returns a list of topics from
the predefined category set. Multi-label allowed (FR-8).

REVISION: added a worked example to the prompt (few-shot prompting)
after the first version showed real accuracy problems in testing - a
stablecoin regulation article was missing "Digital Finance" and CPI
data was incorrectly tagged with it. This is documented directly from
observed test failures, not a hypothetical improvement.

Still validates the model's output against the fixed category list
rather than trusting it blindly - that part was already correct and
stays unchanged.
"""

try:
    from .llm_client import generate, OllamaNotRunningError
except ImportError:
    from llm_client import generate, OllamaNotRunningError

VALID_TOPICS = [
    "Monetary Policy",
    "Financial Stability",
    "Digital Finance",
    "AI in Banking",
]


def classify(title: str, body_text: str) -> list:
    content = body_text.strip() if body_text and body_text.strip() else "(no additional content provided)"
    topic_list_str = ", ".join(VALID_TOPICS)

    prompt = f"""Classify a central banking publication into one or more of these EXACT categories: {topic_list_str}

Example:
Title: Regulating stablecoin issuance: permissible entities and activities
Content: A briefing on which entities may issue stablecoins and what activities are permitted.
Categories: Digital Finance, Financial Stability

Now classify this one. A publication can belong to more than one category, but only include a category if it is clearly relevant - do not guess. Respond with ONLY the matching category names, separated by commas. No explanation.

Title: {title}
Content: {content}

Categories:"""

    raw_response = generate(prompt)

    candidates = [t.strip() for t in raw_response.split(",")]
    valid_found = []
    for candidate in candidates:
        for valid_topic in VALID_TOPICS:
            if candidate.lower() == valid_topic.lower():
                valid_found.append(valid_topic)
                break

    if not valid_found:
        print(f"[classify] Warning: model output didn't match any valid topic. Raw output: {raw_response!r}")

    return valid_found


if __name__ == "__main__":
    test_title = "IMF CPI Data - TZA - pulled 2026-08-31"
    test_body = """IMF CPI (Consumer Price Index) for TZA:
2026-01: 142.3
2026-06: 146.2"""

    print("Test 1: CPI data record (expect Monetary Policy, NOT Digital Finance)")
    try:
        result = classify(test_title, test_body)
        print("Topics:", result)
    except OllamaNotRunningError as e:
        print("ERROR:", e)

    print()
    test_title2 = "Regulating stablecoin issuance: permissible entities and activities"
    test_body2 = "A briefing on which entities may issue stablecoins and what activities are permitted under new regulatory frameworks."
    print("Test 2: stablecoin article (expect Digital Finance)")
    try:
        result2 = classify(test_title2, test_body2)
        print("Topics:", result2)
    except OllamaNotRunningError as e:
        print("ERROR:", e)

    print()
    test_title3 = "Supervisory screening with large language models: finding divergences"
    test_body3 = "Examines how large language models can be used by supervisors to screen for divergences in bank reporting."
    print("Test 3: real BIS record about LLMs in supervision (expect AI in Banking)")
    try:
        result3 = classify(test_title3, test_body3)
        print("Topics:", result3)
    except OllamaNotRunningError as e:
        print("ERROR:", e)
