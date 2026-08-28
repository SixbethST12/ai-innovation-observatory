"""
Normalizer.

Ensures every RawPublication, regardless of which source produced it,
is actually usable before it goes further down the pipeline. This is
NOT about reshaping data (that already happened inside each source
client) - it's about catching the messy edge cases real sources produce:
missing titles, empty URLs, whitespace-only fields.

FR-3 requires metadata capture; a record with no title or no URL isn't
usable metadata, so it gets dropped here rather than silently stored.
"""

from typing import List

try:
    from ..models import RawPublication
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import RawPublication


def normalize(records: List[RawPublication]) -> List[RawPublication]:
    """
    Clean and validate a list of raw records. Returns only records
    that pass basic quality checks - drops anything unusable.
    """
    valid_records = []

    for record in records:
        record.title = record.title.strip()
        record.source_url = record.source_url.strip()

        if not record.title:
            print(f"[normalizer] Dropped record with empty title from {record.institution}")
            continue

        if not record.source_url:
            print(f"[normalizer] Dropped record with empty URL: '{record.title}'")
            continue

        valid_records.append(record)

    return valid_records


if __name__ == "__main__":
    # Self-test with fake good and bad records
    from datetime import datetime

    good = RawPublication(
        title="  Real Publication  ",   # deliberately has extra whitespace
        institution="TEST",
        source_url="https://example.com/real",
        published_date=datetime.now(),
    )
    bad_no_title = RawPublication(
        title="   ",
        institution="TEST",
        source_url="https://example.com/no-title",
        published_date=datetime.now(),
    )
    bad_no_url = RawPublication(
        title="Has Title No URL",
        institution="TEST",
        source_url="",
        published_date=datetime.now(),
    )

    results = normalize([good, bad_no_title, bad_no_url])
    print(f"\n{len(results)} valid record(s) survived out of 3 input records")
    for r in results:
        print("-", repr(r.title), "|", r.source_url)
