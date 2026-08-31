"""
IMF source client - Consumer Price Index (CPI) data.

IMPORTANT DESIGN NOTE: IMF does not have a working publications/RSS
feed (confirmed - old feed URLs are dead, imf.org/en/news/rss is
JavaScript-rendered with no discoverable feed). What IMF DOES have is
a real, documented statistical data API (SDMX), confirmed against a
live example with real sample output:
  https://bd-econ.com/imfapi2.html

This is fundamentally different data than BIS/World Bank/CBK - it's
numeric time-series (CPI values), not documents with their own titles
and URLs. This client pulls real CPI data for Tanzania and regional
peers, then packages the ENTIRE PULL as one synthetic publication-like
record - a genuine stretch of RawPublication's shape, done deliberately
and documented here rather than silently.

Endpoint pattern (confirmed working, Jan 2026 documentation):
  https://api.imf.org/external/sdmx/3.0/data/dataflow/{agency}/{dataflow}/{version}/{key}
Gotchas confirmed from documentation:
  - version wildcard is "~" not "*" (using * causes a 500 error)
  - country codes must be ISO alpha-3 (TZA, not TZ)
  - an invalid code returns HTTP 200 with zero data rows - not an error
"""

from datetime import datetime
from typing import List
import csv
import io
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


class IMFClient(SourceClient):
    institution = "IMF"

    BASE_URL = "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/~/"
    # Tanzania, Kenya, Uganda - CPI, All items, Index, Monthly
    KEY = "TZA+KEN+UGA.CPI._T.IX.M"

    def fetch(self) -> List[RawPublication]:
        url = f"{self.BASE_URL}{self.KEY}"
        params = {"c[TIME_PERIOD]": "ge:2024-01"}
        response = requests.get(url, params=params, headers={"Accept": "text/csv"}, timeout=15)
        response.raise_for_status()

        reader = csv.DictReader(io.StringIO(response.text))
        rows = list(reader)

        if not rows:
            # Confirmed possible per docs: invalid codes return 200 with 0 rows
            print("[IMF] Query returned 0 rows - check country/indicator codes")
            return []

        # Package the whole pull as one record, since this is time-series
        # data, not a set of individual documents.
        lines = [f"{r.get('COUNTRY', '?')} {r.get('TIME_PERIOD', '?')}: {r.get('OBS_VALUE', '?')}" for r in rows[-15:]]
        summary_text = "IMF CPI (Consumer Price Index) data for Tanzania, Kenya, Uganda:\n" + "\n".join(lines)

        today = datetime.now().strftime("%Y-%m-%d")
        record = RawPublication(
            title=f"IMF CPI Data Update - TZA/KEN/UGA - pulled {today}",
            institution=self.institution,
            source_url=f"{url}?asof={today}",   # date included so each day's pull is a distinct record
            published_date=datetime.now(),
            document_type="economic_data",
            body_text=summary_text,
            raw_metadata={"row_count": len(rows), "dataflow": "CPI"},
        )
        return [record]


if __name__ == "__main__":
    # Run directly to see real IMF CPI data: python3 imf.py
    client = IMFClient()
    records = client.safe_fetch()
    print(f"Fetched {len(records)} record(s) from IMF")
    for r in records:
        print("-", r.title)
        print(r.body_text)
