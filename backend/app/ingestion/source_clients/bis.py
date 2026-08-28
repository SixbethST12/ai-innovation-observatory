"""
BIS (Bank for International Settlements) source client.

BIS publishes an RSS feed covering publications, speeches, and press
releases. FR-1 names BIS as one of the mandatory sources; EIR-1 says
access is via API, RSS, or web page — BIS's case is RSS.
"""

from datetime import datetime
from typing import List
import feedparser

try:
    from ..base_client import SourceClient
    from ..models import RawPublication
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_client import SourceClient
    from models import RawPublication


class BISClient(SourceClient):
    institution = "BIS"

    FEED_URL = "https://www.bis.org/doclist/rss_all_categories.rss"

    def fetch(self) -> List[RawPublication]:
        feed = feedparser.parse(self.FEED_URL)
        results = []

        for entry in feed.entries:
            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime(*entry.published_parsed[:6])

            results.append(
                RawPublication(
                    title=entry.get("title", "").strip(),
                    institution=self.institution,
                    source_url=entry.get("link", ""),
                    published_date=published,
                    document_type="publication",
                    body_text=entry.get("summary", ""),
                    raw_metadata={"feed_source": self.FEED_URL},
                )
            )
        return results


if __name__ == "__main__":
    # Run this directly to see real BIS publications: python3 bis.py
    client = BISClient()
    records = client.safe_fetch()
    print(f"Fetched {len(records)} records from BIS")
    for r in records[:3]:
        print("-", r.title, "|", r.source_url)
