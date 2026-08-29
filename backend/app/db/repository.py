"""
Repository - the only place raw database queries happen.

Ingestion code (dedup.py, pipeline.py) calls these functions instead
of touching SQLAlchemy directly. This keeps the database layer
swappable (SQLite -> PostgreSQL later, per EIR-3) without changing
any ingestion code.
"""

try:
    from .database import get_session
    from .db_models import Publication
except ImportError:
    from database import get_session
    from db_models import Publication


def publication_exists(content_hash: str) -> bool:
    """Real dedup check - replaces dedup.py's placeholder is_duplicate()."""
    session = get_session()
    try:
        exists = session.query(Publication).filter_by(content_hash=content_hash).first() is not None
        return exists
    finally:
        session.close()


def save_publication(raw_publication) -> bool:
    """
    Inserts one RawPublication (from models.py) into the database.
    Returns True if saved, False if it already existed (safety net -
    should rarely trigger since dedup.py filters before this is called).
    """
    if publication_exists(raw_publication.content_hash):
        return False

    session = get_session()
    try:
        record = Publication(
            title=raw_publication.title,
            institution=raw_publication.institution,
            source_url=raw_publication.source_url,
            published_date=raw_publication.published_date,
            document_type=raw_publication.document_type,
            body_text=raw_publication.body_text,
            content_hash=raw_publication.content_hash,
        )
        session.add(record)
        session.commit()
        return True
    finally:
        session.close()


def count_publications() -> int:
    session = get_session()
    try:
        return session.query(Publication).count()
    finally:
        session.close()


if __name__ == "__main__":
    from datetime import datetime
    try:
        from .database import engine
        from .database import Base
    except ImportError:
        from database import engine, Base

    Base.metadata.create_all(engine)  # ensure table exists

    print(f"Publications in DB before: {count_publications()}")

    class FakeRecord:
        title = "Self-Test Record"
        institution = "TEST"
        source_url = "https://example.com/self-test"
        published_date = datetime.now()
        document_type = "publication"
        body_text = ""
        content_hash = "test-hash-12345"

    saved = save_publication(FakeRecord())
    print(f"First save attempt: {'saved' if saved else 'skipped (duplicate)'}")

    saved_again = save_publication(FakeRecord())
    print(f"Second save attempt (same record): {'saved' if saved_again else 'skipped (duplicate)'}")

    print(f"Publications in DB after: {count_publications()}")
