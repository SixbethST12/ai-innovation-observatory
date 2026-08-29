"""
Dedup.

Two responsibilities:
  1. Fingerprint each record (fully working now) - uses the
     content_hash property already built into RawPublication.
  2. Check that fingerprint against stored records (NOT yet wired to
     a real database - db/ doesn't exist yet). is_duplicate() below
     is a placeholder that always returns False until the database
     layer is built; this will be replaced with a real query then.

This satisfies FR-4 (detect and discard duplicates) once the
placeholder is replaced with a real DB check.
"""

from typing import List

try:
    from ..models import RawPublication
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import RawPublication


def is_duplicate(content_hash: str) -> bool:
    """
    PLACEHOLDER - always returns False for now.
    Once db/ exists, this will query the publications table:
        SELECT 1 FROM publications WHERE content_hash = ? LIMIT 1
    """
    return False


def deduplicate(records: List[RawPublication]) -> List[RawPublication]:
    """
    Filters out records already seen - either duplicates within this
    same batch (two sources reporting the same URL), or records
    already stored (once is_duplicate() is real).
    """
    seen_hashes = set()
    unique_records = []

    for record in records:
        h = record.content_hash

        if h in seen_hashes:
            print(f"[dedup] Skipped duplicate within batch: '{record.title}'")
            continue

        if is_duplicate(h):
            print(f"[dedup] Skipped - already in database: '{record.title}'")
            continue

        seen_hashes.add(h)
        unique_records.append(record)

    return unique_records


if __name__ == "__main__":
    from datetime import datetime

    record_a = RawPublication(
        title="Publication A",
        institution="TEST",
        source_url="https://example.com/a",
        published_date=datetime.now(),
    )
    record_a_duplicate = RawPublication(
        title="Publication A (same URL, different title text)",
        institution="TEST",
        source_url="https://example.com/a",   # same URL -> same hash
        published_date=datetime.now(),
    )
    record_b = RawPublication(
        title="Publication B",
        institution="TEST",
        source_url="https://example.com/b",
        published_date=datetime.now(),
    )

    results = deduplicate([record_a, record_a_duplicate, record_b])
    print(f"\n{len(results)} unique record(s) survived out of 3 input records")
    for r in results:
        print("-", r.title)
