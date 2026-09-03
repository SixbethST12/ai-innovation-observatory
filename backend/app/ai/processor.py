"""
AI processor - orchestrates summarize + classify + relevance for real
stored publications, writes results back to the database.

Default batch size is small (5) deliberately - each record needs 3
separate Ollama calls, and on limited CPU hardware each call takes
several seconds. Processing all 174 stored records at once could
take 30-60+ minutes. Start small, confirm correctness, scale up.
"""

import time

try:
    from .summarize import summarize
    from .classify import classify
    from .relevance import assess_relevance
    from .llm_client import OllamaNotRunningError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from summarize import summarize
    from classify import classify
    from relevance import assess_relevance
    from llm_client import OllamaNotRunningError

try:
    from ..db.repository import get_unprocessed_publications, save_ai_results
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.repository import get_unprocessed_publications, save_ai_results


def process_batch(limit: int = 5):
    """
    Fetches up to `limit` unprocessed publications, runs all three AI
    tasks on each, saves results back to the database.
    """
    records = get_unprocessed_publications(limit=limit)

    if not records:
        print("No unprocessed records found - nothing to do.")
        return

    print(f"Processing {len(records)} record(s)...\n")

    for i, record in enumerate(records, 1):
        start = time.time()
        print(f"[{i}/{len(records)}] {record.institution} | {record.title[:60]}")

        try:
            summary = summarize(record.title, record.body_text)
            topics = classify(record.title, record.body_text)
            relevance = assess_relevance(record.title, record.body_text)

            save_ai_results(record.id, summary, topics, relevance)

            elapsed = time.time() - start
            print(f"  -> Summary: {summary[:80]}...")
            print(f"  -> Topics: {topics}")
            print(f"  -> Relevance: {relevance[:80]}...")
            print(f"  -> Done in {elapsed:.1f}s\n")

        except OllamaNotRunningError as e:
            print(f"  -> STOPPED: {e}")
            break


if __name__ == "__main__":
    process_batch(limit=5)
