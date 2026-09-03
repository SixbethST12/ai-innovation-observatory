"""
AI processor - orchestrates summarize + classify + relevance for real
stored publications, writes results back to the database.

FIX (following the same real incident documented in llm_client.py):
now distinguishes OllamaTimeoutError (skip this one record, continue
to the next - it stays unprocessed and will be retried next cycle)
from OllamaNotRunningError (Ollama is completely down - stop the
whole batch, since every subsequent call would fail the same way).
Previously, a timeout on ONE record crashed the entire scheduler.
"""

import time

try:
    from .summarize import summarize
    from .classify import classify
    from .relevance import assess_relevance
    from .llm_client import OllamaNotRunningError, OllamaTimeoutError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from summarize import summarize
    from classify import classify
    from relevance import assess_relevance
    from llm_client import OllamaNotRunningError, OllamaTimeoutError

try:
    from ..db.repository import get_unprocessed_publications, save_ai_results
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.repository import get_unprocessed_publications, save_ai_results


def process_batch(limit: int = 5):
    records = get_unprocessed_publications(limit=limit)

    if not records:
        print("No unprocessed records found - nothing to do.")
        return

    print(f"Processing {len(records)} record(s)...\n")
    skipped_count = 0

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

        except OllamaTimeoutError as e:
            print(f"  -> SKIPPED (timeout): {e}\n")
            skipped_count += 1
            continue

        except OllamaNotRunningError as e:
            print(f"  -> STOPPED (Ollama down): {e}")
            break

    if skipped_count:
        print(f"Note: {skipped_count} record(s) skipped due to timeout - will retry next cycle.")


if __name__ == "__main__":
    process_batch(limit=5)
