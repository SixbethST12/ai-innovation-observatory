"""
Topic classification - FR-7, FR-8, NFR-7.

UPGRADED: categories now come from the database (categories table)
instead of a hardcoded Python list. This is what makes NFR-7's
"configurable without code redeployment" genuinely true - adding a
new category means an INSERT into the categories table, not editing
this file. Expanded from 4 to 11 categories per updated requirements.

Still validates the model's output against the current valid category
list rather than trusting it blindly - unchanged from before.
"""

try:
    from .llm_client import generate, OllamaNotRunningError, OllamaTimeoutError
except ImportError:
    from llm_client import generate, OllamaNotRunningError, OllamaTimeoutError

try:
    from ..db.repository import get_active_categories
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.repository import get_active_categories


def classify(title: str, body_text: str) -> list:
    """
    Returns a list of 1+ topics from the current active categories
    (read fresh from the database each call, not cached, so a newly
    added category is picked up immediately without restarting anything).
    """
    valid_topics = get_active_categories()
    if not valid_topics:
        print("[classify] Warning: no active categories found in database")
        return []

    content = body_text.strip() if body_text and body_text.strip() else "(no additional content provided)"
    topic_list_str = ", ".join(valid_topics)

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
        for valid_topic in valid_topics:
            if candidate.lower() == valid_topic.lower():
                valid_found.append(valid_topic)
                break

    if not valid_found:
        print(f"[classify] Warning: model output didn't match any valid topic. Raw output: {raw_response!r}")

    return valid_found


if __name__ == "__main__":
    print(f"Active categories: {get_active_categories()}")
    print()

    test_title = "Regulating stablecoin issuance: permissible entities and activities"
    test_body = "A briefing on which entities may issue stablecoins and what activities are permitted under new regulatory frameworks."
    print("Test 1: stablecoin article")
    try:
        result = classify(test_title, test_body)
        print("Topics:", result)
    except (OllamaNotRunningError, OllamaTimeoutError) as e:
        print("ERROR:", e)

    print()
    test_title2 = "Central bank cybersecurity framework for payment systems"
    test_body2 = "New guidance on protecting critical payment infrastructure from cyber threats, covering both retail and wholesale payment systems."
    print("Test 2: cybersecurity + payment systems article (new categories)")
    try:
        result2 = classify(test_title2, test_body2)
        print("Topics:", result2)
    except (OllamaNotRunningError, OllamaTimeoutError) as e:
        print("ERROR:", e)
