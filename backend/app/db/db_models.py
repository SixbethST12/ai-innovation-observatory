"""
Publication table schema.

Mirrors RawPublication's fields (models.py) plus what only makes
sense once something is actually stored: a primary key id, the
content_hash used for dedup (FR-4), a fetched_at timestamp
(NFR-9, auditability), and a processed flag the AI layer will use
later to find unprocessed records.

summary / topic / relevance_note are nullable and unused for now -
they exist so the schema doesn't need to change again once the AI
layer starts writing to this same table (NFR-8: traceability - AI
output stays on the same row as its source record, never separate).
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime

try:
    from .database import Base
except ImportError:
    from database import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    published_date = Column(DateTime, nullable=True)
    document_type = Column(String, default="publication")
    body_text = Column(Text, default="")

    content_hash = Column(String, unique=True, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    # AI layer fields - unused for now, filled in later stage
    processed = Column(Boolean, default=False)
    summary = Column(Text, nullable=True)
    relevance_note = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)  # comma-separated, e.g. "Monetary Policy,Financial Stability"

    def __repr__(self):
        return f"<Publication id={self.id} institution={self.institution} title={self.title[:40]!r}>"


if __name__ == "__main__":
    # Self-test: actually create the table in the database
    try:
        from .database import engine
    except ImportError:
        from database import engine

    Base.metadata.create_all(engine)
    print("Table 'publications' created (or already exists)")

    # Confirm the table is really there by inspecting the database
    from sqlalchemy import inspect
    inspector = inspect(engine)
    print("Tables in database:", inspector.get_table_names())
    print("Columns in 'publications':")
    for col in inspector.get_columns("publications"):
        print(f"  - {col['name']} ({col['type']})")

class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False)
    time_window = Column(String, nullable=False)  # e.g. "2026-08" (year-month)
    publication_count = Column(Integer, default=0)
    is_emerging = Column(Boolean, default=False)
    computed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trend topic={self.topic} window={self.time_window} count={self.publication_count} emerging={self.is_emerging}>"

