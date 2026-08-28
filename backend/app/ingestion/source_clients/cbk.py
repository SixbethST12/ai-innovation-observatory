"""
Central Bank of Kenya (CBK) source client.

CBK does not publish a documented API or an advertised RSS feed
(confirmed by inspecting their site directly). However, their site
runs on WordPress (confirmed via wp-content/ paths and the default
WordPress permalink pattern in their news URLs), and WordPress sites
auto-generate an RSS feed at /feed/ even when it isn't linked anywhere
visible. Verified working at:
  https://www.centralbank.go.ke/feed/

This is a peer central bank per FR-1's "peer central banks" category,
included via RSS rather than web-scraping since a real feed exists.
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


class CBKClient(SourceClient):
    institution = "Central Bank of Kenya"

    FEED_URL = "https://www.centralbank.go.ke/feed/"

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
    # Run directly to see real CBK items: python3 cbk.py
    client = CBKClient()
    records = client.safe_fetch()
    print(f"Fetched {len(records)} records from Central Bank of Kenya")
    for r in records[:3]:
        print("-", r.title, "|", r.source_url)
