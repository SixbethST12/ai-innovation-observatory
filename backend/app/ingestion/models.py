"""
Standard publication record shape.

Every source client (BIS, IMF, World Bank...) must return data in
this shape, regardless of whether the source is RSS or a REST API.
This is what makes normalization, dedup, and storage source-agnostic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class RawPublication:
    title: str
    institution: str          # "BIS", "IMF", "World Bank"
    source_url: str
    published_date: Optional[datetime]
    document_type: str = "publication"
    body_text: str = ""
    raw_metadata: dict = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Unique fingerprint used for dedup (FR-4)."""
        key = self.source_url or f"{self.title}|{self.published_date}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    # Quick manual test — run this file directly to confirm it works:
    #   python models.py
    test_record = RawPublication(
        title="Test Publication",
        institution="BIS",
        source_url="https://www.bis.org/example",
        published_date=datetime.now(),
    )
    print("Title:", test_record.title)
    print("Hash:", test_record.content_hash)