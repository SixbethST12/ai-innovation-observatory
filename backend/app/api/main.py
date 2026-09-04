"""
REST API - EIR-2 (web-based dashboard/search interface, backend half).

Exposes stored publications, search, and trends as public JSON
endpoints, plus a protected admin section (NFR-2: admin functions
require authentication).
"""

from fastapi import FastAPI, Query, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import jwt

try:
    from ..db.repository import (
        get_publications, search_publications, get_trends, get_publication_by_id,
        get_user_by_username, count_publications, count_processed,
    )
    from .auth import verify_password, create_token, decode_token
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.repository import (
        get_publications, search_publications, get_trends, get_publication_by_id,
        get_user_by_username, count_publications, count_processed,
    )
    from auth import verify_password, create_token, decode_token

app = FastAPI(
    title="AI Innovation Observatory API",
    description="Central Banking & Financial Sector Intelligence - Bank of Tanzania student project",
    version="0.3.0",
)


class LoginRequest(BaseModel):
    username: str
    password: str


def require_admin(authorization: Optional[str] = Header(default=None)):
    """
    FastAPI dependency - runs before any endpoint that includes it,
    checks for a valid 'Authorization: Bearer <token>' header.
    Raises 401 if missing, malformed, or the token is invalid/expired.
    This is what actually implements NFR-2 on any endpoint that uses it.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired - please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload  # {"sub": username, "role": role, "exp": ...}


def publication_to_dict(pub):
    return {
        "id": pub.id,
        "title": pub.title,
        "institution": pub.institution,
        "source_url": pub.source_url,
        "published_date": pub.published_date.isoformat() if pub.published_date else None,
        "document_type": pub.document_type,
        "body_text": pub.body_text,
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


# --- Public endpoints ---

@app.get("/publications")
def list_publications(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    topic: Optional[str] = None,
    institution: Optional[str] = None,
):
    pubs = get_publications(limit=limit, offset=offset, topic=topic, institution=institution)
    return {"count": len(pubs), "results": [publication_to_dict(p) for p in pubs]}


@app.get("/publications/{publication_id}")
def get_publication(publication_id: int):
    pub = get_publication_by_id(publication_id)
    if pub is None:
        raise HTTPException(status_code=404, detail=f"Publication {publication_id} not found")
    return publication_to_dict(pub)


@app.get("/search")
def search(q: str = Query(..., min_length=2), limit: int = Query(default=20, le=100)):
    results = search_publications(keyword=q, limit=limit)
    return {"query": q, "count": len(results), "results": [publication_to_dict(p) for p in results]}


@app.get("/trends")
def list_trends(emerging_only: bool = Query(default=False)):
    trends = get_trends()
    if emerging_only:
        trends = [t for t in trends if t.is_emerging]
    return {"count": len(trends), "results": [trend_to_dict(t) for t in trends]}


# --- Auth ---

@app.post("/auth/login")
def login(credentials: LoginRequest):
    """Verifies username/password, returns a JWT token valid for 24 hours."""
    user = get_user_by_username(credentials.username)
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_token(username=user.username, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# --- Protected admin endpoints (NFR-2) ---

@app.get("/admin/stats")
def admin_stats(current_user: dict = Depends(require_admin)):
    """
    Admin-only system stats. Requires a valid Bearer token (NFR-2).
    Proves authentication is actually enforced, not just present.
    """
    total = count_publications()
    processed = count_processed()
    return {
        "authenticated_as": current_user["sub"],
        "role": current_user["role"],
        "total_publications": total,
        "processed": processed,
        "unprocessed": total - processed,
    }
