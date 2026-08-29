"""
Dedup.

Two responsibilities:
  1. Fingerprint each record - uses the content_hash property already
     built into RawPublication.
  2. Check that fingerprint against stored records - now wired to the
     real database via db/repository.py.

Satisfies FR-4 (detect and discard duplicates).
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
    """Real DB-backed dedup check."""
    try:
        from ...db.repository import publication_exists
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from db.repository import publication_exists
    return publication_exists(content_hash)


def deduplicate(records: List[RawPublication]) -> List[RawPublication]:
    """
    Filters out records already seen - either duplicates within this
    same batch, or records already stored in the database.
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
        source_url="https://example.com/a",
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
