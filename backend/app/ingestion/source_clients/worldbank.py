"""
World Bank source client.

Unlike BIS/IMF, this uses the World Bank's public Documents & Reports
API (JSON over REST) rather than RSS. Verified directly against a live
response before writing this client:
  https://search.worldbank.org/api/v3/wds?format=json&qterm=wind%20turbine&fl=docdt,count

Key things confirmed from that real response (not assumed):
  - "rows" and "os" (offset) are real, documented parameters; default
    rows=10, default os=0. No "order" parameter is documented anywhere,
    so it is deliberately NOT used here.
  - The "documents" object in the response contains a "facets" key
    alongside the actual document entries — this is NOT a real record
    and must be explicitly skipped, or it produces a fake empty result.
  - "abstracts" is not always present on every document.
  - Date format is ISO 8601 with a trailing "Z", e.g. "2006-04-24T04:00:00Z".
"""

from datetime import datetime
from typing import List
import requests

try:
    from ..base_client import SourceClient
    from ..models import RawPublication
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base_client import SourceClient
    from models import RawPublication


class WorldBankClient(SourceClient):
    institution = "World Bank"

    API_URL = "https://search.worldbank.org/api/v3/wds"
    DEFAULT_PARAMS = {
        "format": "json",
        "qterm": "central bank",
        "rows": 60,
    }

    def fetch(self) -> List[RawPublication]:
        response = requests.get(self.API_URL, params=self.DEFAULT_PARAMS, timeout=15)
        response.raise_for_status()
        data = response.json()

        documents = data.get("documents", {})
        results = []

        for doc_id, doc in documents.items():
            if doc_id == "facets" or not isinstance(doc, dict):
                continue
            if "display_title" not in doc:
                continue

            published = None
            if doc.get("docdt"):
                try:
                    published = datetime.fromisoformat(doc["docdt"][:10])
                except ValueError:
                    published = None

            abstract = ""
            if isinstance(doc.get("abstracts"), dict):
                abstract = doc["abstracts"].get("cdata!", "")

            results.append(
                RawPublication(
                    title=doc.get("display_title", "").strip(),
                    institution=self.institution,
                    source_url=doc.get("pdfurl") or doc.get("url", ""),
                    published_date=published,
                    document_type=doc.get("docty", "publication"),
                    body_text=abstract,
                    raw_metadata={"wb_doc_id": doc_id},
                )
            )
        return results


if __name__ == "__main__":
    client = WorldBankClient()
    records = client.safe_fetch()
    print(f"Fetched {len(records)} records from World Bank")
    for r in records[:6]:
        print("-", r.title, "|", r.source_url)
