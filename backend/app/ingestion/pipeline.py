"""
Pipeline.

Wires the full ingestion sequence together:
    Registry (fetch all sources) -> Normalize -> Dedup -> Store

This is the complete ingestion layer running as one system against
REAL data from BIS, World Bank, and CBK, ending in real persistence
to the database (FR-1 through FR-4 all covered here).
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


def store_records(records: List[RawPublication]) -> int:
    """Saves records to the database. Returns count of newly saved records."""
    try:
        from ..db.repository import save_publication
        from ..db.database import engine, Base
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from db.repository import save_publication
        from db.database import engine, Base

    Base.metadata.create_all(engine)

    saved_count = 0
    for record in records:
        if save_publication(record):
            saved_count += 1
    return saved_count


if __name__ == "__main__":
    final_records = run_ingestion()

    print("\n=== STAGE 4: STORE ===")
    saved = store_records(final_records)
    print(f"Newly saved to database: {saved}")
    print(f"Already existed (skipped): {len(final_records) - saved}")

    print("\n=== PIPELINE COMPLETE ===")
    print(f"{len(final_records)} clean, unique records processed")
