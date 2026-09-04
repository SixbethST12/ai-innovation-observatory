"""
IMF source client - Consumer Price Index (CPI) data, one record per country.

FIX (real bug found via API testing): titles/body_text previously used
only bare ISO alpha-3 codes (e.g. "ETH", "RWA"). Downstream AI
functions had no way to know these were country codes, and genuinely
hallucinated - "ETH" was summarized as "Ethereum" (the cryptocurrency)
instead of Ethiopia; "RWA" as "the region west of Afghanistan" instead
of Rwanda. Fixed by embedding the full country name directly in both
title and body_text, removing the ambiguity at the source rather than
patching every AI prompt separately.
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

COUNTRY_NAMES = {
    "TZA": "Tanzania", "KEN": "Kenya", "UGA": "Uganda", "RWA": "Rwanda", "BDI": "Burundi",
    "ZAF": "South Africa", "NGA": "Nigeria", "EGY": "Egypt", "GHA": "Ghana", "ETH": "Ethiopia",
    "MOZ": "Mozambique", "ZMB": "Zambia", "USA": "United States", "GBR": "United Kingdom",
    "CHN": "China", "IND": "India", "BRA": "Brazil", "JPN": "Japan", "DEU": "Germany",
    "FRA": "France", "MEX": "Mexico", "ARG": "Argentina", "CHL": "Chile", "COL": "Colombia",
    "PER": "Peru", "ITA": "Italy", "ESP": "Spain", "NLD": "Netherlands", "SWE": "Sweden",
    "CHE": "Switzerland", "IDN": "Indonesia", "KOR": "South Korea", "THA": "Thailand",
    "VNM": "Vietnam", "PHL": "Philippines", "SAU": "Saudi Arabia", "ARE": "United Arab Emirates",
    "TUR": "Turkey", "AUS": "Australia", "MAR": "Morocco",
}


class IMFClient(SourceClient):
    institution = "IMF"

    BASE_URL = "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/~/"
    COUNTRIES = list(COUNTRY_NAMES.keys())
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

        for country_code, country_rows in by_country.items():
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            recent = country_rows[-6:]
            lines = [f"{r.get('TIME_PERIOD', '?')}: {r.get('OBS_VALUE', '?')}" for r in recent]
            body = f"IMF Consumer Price Index (CPI) data for {country_name} (ISO code: {country_code}):\n" + "\n".join(lines)

            record = RawPublication(
                title=f"IMF CPI Data - {country_name} ({country_code}) - pulled {today}",
                institution=self.institution,
                source_url=f"{url}?country={country_code}&asof={today}",
                published_date=datetime.now(),
                document_type="economic_data",
                body_text=body,
                raw_metadata={"country_code": country_code, "country_name": country_name, "row_count": len(country_rows), "dataflow": "CPI"},
            )
            results.append(record)

        print(f"[IMF] {len(rows)} total rows returned, covering {len(by_country)} of {len(self.COUNTRIES)} requested countries")
        return results


if __name__ == "__main__":
    client = IMFClient()
    records = client.safe_fetch()
    print(f"\nFetched {len(records)} record(s) from IMF")
    for r in records[:3]:
        print("-", r.title)
        print(" ", r.body_text.split(chr(10))[0])
