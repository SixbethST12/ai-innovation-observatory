"""
REST API - EIR-2 (web-based dashboard/search interface, backend half).

Exposes stored publications, search, and trends as JSON endpoints.
This is the bridge between everything already built (ingestion, AI
layer, trend detection) and any future frontend (FR-13/FR-14
dashboard, FR-15/FR-16 search) - the frontend will call these
endpoints instead of touching the database directly.
"""

from fastapi import FastAPI, Query
from typing import Optional

try:
    from ..db.repository import get_publications, search_publications, get_trends
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.repository import get_publications, search_publications, get_trends

app = FastAPI(
    title="AI Innovation Observatory API",
    description="Central Banking & Financial Sector Intelligence - Bank of Tanzania student project",
    version="0.1.0",
)


def publication_to_dict(pub):
    """Converts a SQLAlchemy Publication row into a plain dict for JSON."""
    return {
        "id": pub.id,
        "title": pub.title,
        "institution": pub.institution,
        "source_url": pub.source_url,
        "published_date": pub.published_date.isoformat() if pub.published_date else None,
        "document_type": pub.document_type,
        "summary": pub.summary,
        "topics": pub.topics.split(", ") if pub.topics else [],
        "relevance_note": pub.relevance_note,
        "processed": pub.processed,
        "ai_generated_disclaimer": "Summary, topics, and relevance assessment are AI-generated (NFR-12) and do not represent an official Bank of Tanzania position." if pub.processed else None,
    }


def trend_to_dict(trend):
    return {
        "topic": trend.topic,
        "time_window": trend.time_window,
        "publication_count": trend.publication_count,
        "is_emerging": trend.is_emerging,
        "computed_at": trend.computed_at.isoformat() if trend.computed_at else None,
    }


@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Innovation Observatory API"}


@app.get("/publications")
def list_publications(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    topic: Optional[str] = None,
    institution: Optional[str] = None,
):
    """FR-13/FR-14: dashboard feed, filterable by topic and institution."""
    pubs = get_publications(limit=limit, offset=offset, topic=topic, institution=institution)
    return {"count": len(pubs), "results": [publication_to_dict(p) for p in pubs]}


@app.get("/search")
def search(q: str = Query(..., min_length=2), limit: int = Query(default=20, le=100)):
    """FR-15/FR-16: keyword search across title, summary, relevance_note."""
    results = search_publications(keyword=q, limit=limit)
    return {"query": q, "count": len(results), "results": [publication_to_dict(p) for p in results]}


@app.get("/trends")
def list_trends():
    """FR-9/FR-10: computed topic trends, most recent first."""
    trends = get_trends()
    return {"count": len(trends), "results": [trend_to_dict(t) for t in trends]}
