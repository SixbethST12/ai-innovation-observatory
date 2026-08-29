"""
Pipeline.

Wires the full ingestion sequence together:
    Registry (fetch all sources) -> Normalize -> Dedup

This is the first time all three pieces run together against REAL
data pulled live from BIS, World Bank, and CBK - not fake test
records. This is the actual proof the ingestion layer works as one
system, not just as isolated tested pieces.

Does NOT yet write to a database - db/ doesn't exist yet. This stops
at "here are the clean, deduplicated records ready to store"
(FR-1 through FR-4 covered here; storage is the next stage).
"""

from typing import List

try:
    from .source_clients import ALL_CLIENTS
    from .processing.normalizer import normalize
    from .processing.dedup import deduplicate
    from .models import RawPublication
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from source_clients import ALL_CLIENTS
    from processing.normalizer import normalize
    from processing.dedup import deduplicate
    from models import RawPublication


def run_ingestion() -> List[RawPublication]:
    """Fetch from every registered source, normalize, dedup. Returns the final clean list."""
    raw_records = []

    print("=== STAGE 1: FETCH ===")
    for client_class in ALL_CLIENTS:
        client = client_class()
        records = client.safe_fetch()
        print(f"{client.institution}: {len(records)} records")
        raw_records.extend(records)
    print(f"Total raw records: {len(raw_records)}")

    print("\n=== STAGE 2: NORMALIZE ===")
    normalized = normalize(raw_records)
    print(f"Records after normalization: {len(normalized)}")

    print("\n=== STAGE 3: DEDUP ===")
    deduped = deduplicate(normalized)
    print(f"Records after dedup: {len(deduped)}")

    return deduped


if __name__ == "__main__":
    final_records = run_ingestion()
    print("\n=== PIPELINE COMPLETE ===")
    print(f"{len(final_records)} clean, unique records ready for storage")
    print("\nSample:")
    for r in final_records[:5]:
        print("-", r.institution, "|", r.title)
