"""
IMF source client - Consumer Price Index (CPI) data, one record per country.

40 countries total: original 20 (Tanzania/EAC/Africa/major economies)
plus 20 more covering Latin America, Europe, additional Asia, Middle
East, and Oceania - broader global comparison context for BOT.

Endpoint confirmed working, no auth required:
  https://api.imf.org/external/sdmx/3.0/data/dataflow/{agency}/{dataflow}/{version}/{key}
Gotchas confirmed from documentation:
  - version wildcard is "~" not "*"
  - country codes must be ISO alpha-3
  - a country with no data returns 0 rows for that country silently,
    not an error - not every country below is guaranteed to have
    current CPI data available.
"""

from datetime import datetime
from typing import List
from collections import defaultdict
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

    COUNTRIES = [
        # Original 20
        "TZA", "KEN", "UGA", "RWA", "BDI",
        "ZAF", "NGA", "EGY", "GHA", "ETH", "MOZ", "ZMB",
        "USA", "GBR", "CHN", "IND", "BRA", "JPN", "DEU", "FRA",
        # 20 new: Latin America, Europe, Asia, Middle East, Oceania, more Africa
        "MEX", "ARG", "CHL", "COL", "PER",
        "ITA", "ESP", "NLD", "SWE", "CHE",
        "IDN", "KOR", "THA", "VNM", "PHL",
        "SAU", "ARE", "TUR", "AUS", "MAR",
    ]
    KEY = "+".join(COUNTRIES) + ".CPI._T.IX.M"

    def fetch(self) -> List[RawPublication]:
        url = f"{self.BASE_URL}{self.KEY}"
        params = {"c[TIME_PERIOD]": "ge:2024-01"}
        response = requests.get(url, params=params, headers={"Accept": "text/csv"}, timeout=25)
        response.raise_for_status()

        reader = csv.DictReader(io.StringIO(response.text))
        rows = list(reader)

        if not rows:
            print("[IMF] Query returned 0 rows total")
            return []

        by_country = defaultdict(list)
        for r in rows:
            country = r.get("COUNTRY", "?")
            by_country[country].append(r)

        today = datetime.now().strftime("%Y-%m-%d")
        results = []

        for country, country_rows in by_country.items():
            recent = country_rows[-6:]
            lines = [f"{r.get('TIME_PERIOD', '?')}: {r.get('OBS_VALUE', '?')}" for r in recent]
            body = f"IMF CPI (Consumer Price Index) for {country}:\n" + "\n".join(lines)

            record = RawPublication(
                title=f"IMF CPI Data - {country} - pulled {today}",
                institution=self.institution,
                source_url=f"{url}?country={country}&asof={today}",
                published_date=datetime.now(),
                document_type="economic_data",
                body_text=body,
                raw_metadata={"country": country, "row_count": len(country_rows), "dataflow": "CPI"},
            )
            results.append(record)

        print(f"[IMF] {len(rows)} total rows returned, covering {len(by_country)} of {len(self.COUNTRIES)} requested countries")
        return results


if __name__ == "__main__":
    client = IMFClient()
    records = client.safe_fetch()
    print(f"\nFetched {len(records)} record(s) from IMF")
    for r in records:
        print("-", r.title)
