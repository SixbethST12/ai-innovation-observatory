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


def get_unprocessed_publications(limit=10):
    """Returns up to `limit` publications where processed is False."""
    session = get_session()
    try:
        return session.query(Publication).filter_by(processed=False).limit(limit).all()
    finally:
        session.close()


def save_ai_results(publication_id: int, summary: str, topics: list, relevance_note: str):
    """Writes AI-generated results back onto an existing publication row, marks it processed."""
    session = get_session()
    try:
        pub = session.query(Publication).filter_by(id=publication_id).first()
        if pub is None:
            return False
        pub.summary = summary
        pub.topics = ", ".join(topics) if topics else ""
        pub.relevance_note = relevance_note
        pub.processed = True
        session.commit()
        return True
    finally:
        session.close()


def get_publications(limit=20, offset=0, topic=None, institution=None):
    """
    Returns publications, most recently fetched first, optionally
    filtered by topic (partial match, since topics is comma-separated
    text) or institution (exact match). Supports pagination via
    limit/offset - FR-14 (filter by source, topic, date, relevance).
    """
    session = get_session()
    try:
        query = session.query(Publication)
        if topic:
            query = query.filter(Publication.topics.like(f"%{topic}%"))
        if institution:
            query = query.filter(Publication.institution == institution)
        return query.order_by(Publication.fetched_at.desc()).offset(offset).limit(limit).all()
    finally:
        session.close()


def search_publications(keyword: str, limit=20):
    """
    Keyword search across title, summary, and relevance_note - FR-15.
    Simple LIKE-based search (not full-text or semantic) - adequate
    for this project's scale (a few hundred records), documented as
    a simplification rather than pretending it's more sophisticated.
    """
    session = get_session()
    try:
        pattern = f"%{keyword}%"
        return session.query(Publication).filter(
            (Publication.title.like(pattern)) |
            (Publication.summary.like(pattern)) |
            (Publication.relevance_note.like(pattern))
        ).order_by(Publication.fetched_at.desc()).limit(limit).all()
    finally:
        session.close()


def get_trends():
    """Returns all computed trend records, most recent first."""
    try:
        from .db_models import Trend
    except ImportError:
        from db_models import Trend
    session = get_session()
    try:
        return session.query(Trend).order_by(Trend.computed_at.desc()).all()
    finally:
        session.close()


def get_publication_by_id(publication_id: int):
    """Returns a single publication by ID, or None if it doesn't exist."""
    session = get_session()
    try:
        return session.query(Publication).filter_by(id=publication_id).first()
    finally:
        session.close()


def get_user_by_username(username: str):
    """Returns a User by username, or None if not found. Used for login."""
    try:
        from .db_models import User
    except ImportError:
        from db_models import User
    session = get_session()
    try:
        return session.query(User).filter_by(username=username).first()
    finally:
        session.close()


def count_processed():
    """Count of publications where processed=True. Used for admin stats."""
    session = get_session()
    try:
        return session.query(Publication).filter_by(processed=True).count()
    finally:
        session.close()


def get_stats_by_institution():
    """Returns publication counts grouped by institution - for dashboard stat cards."""
    from sqlalchemy import func
    session = get_session()
    try:
        results = session.query(
            Publication.institution, func.count(Publication.id)
        ).group_by(Publication.institution).all()
        return {institution: count for institution, count in results}
    finally:
        session.close()
