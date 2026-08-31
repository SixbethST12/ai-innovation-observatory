"""
BIS (Bank for International Settlements) source client.

IMPORTANT: BIS restructured their site on/around 2026-08-31, breaking
the previous publications RSS feed (bis.org/doclist/*.rss - confirmed
dead via curl, BIS's own server returns a real 404 page for these
paths now). This client instead uses BIS's statistics release
calendar feed (data.bis.org/feed.xml, confirmed live via curl - HTTP
200, real XML), a genuinely different feed covering statistical
release announcements (exchange rates, policy rates, etc.) rather
than narrative publications/speeches.

KNOWN BEHAVIOR: This feed repeats the same link (e.g. .../topics/XRU)
across multiple weekly releases with different pubDate values. Since
content_hash (models.py) hashes on source_url alone, only the FIRST
occurrence of each topic link gets stored - later re-releases of the
same topic are treated as duplicates by design, not by bug. This
means the DB tracks "this release type has been seen" rather than
every individual weekly release event.
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

    FEED_URL = "https://data.bis.org/feed.xml"

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
                    document_type="statistical_release",
                    body_text=entry.get("summary", ""),
                    raw_metadata={"feed_source": self.FEED_URL, "category": entry.get("category", "")},
                )
            )
        return results


if __name__ == "__main__":
    # Run directly to see real BIS statistical release data: python3 bis.py
    client = BISClient()
    records = client.safe_fetch()
    print(f"Fetched {len(records)} records from BIS")
    for r in records[:5]:
        print("-", r.title, "|", r.published_date)
