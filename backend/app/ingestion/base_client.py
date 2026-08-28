"""
Base contract for a source client.

FR-1 requires a *configurable list* of approved sources. That means
adding a new institution should never touch the scheduler or the
parser — it should only mean dropping in one new file under
source_clients/ that implements this interface.
"""

from abc import ABC, abstractmethod
from typing import List

try:
    from .models import RawPublication      # when imported as part of the package
except ImportError:
    from models import RawPublication       # when run directly as a script (testing)


class SourceClient(ABC):
    """Every source (BIS, IMF, World Bank, peer central banks...) implements this."""

    institution: str = "UNKNOWN"

    @abstractmethod
    def fetch(self) -> List[RawPublication]:
        """
        Pull the latest available items from this source and return
        them as a list of RawPublication. Must NOT raise on a single
        malformed item — skip it and continue (NFR-5: one bad source
        must not interrupt collection from others).
        """
        raise NotImplementedError

    def safe_fetch(self) -> List[RawPublication]:
        """
        Wrapper the scheduler actually calls. Isolates failures per
        source so one down feed doesn't kill the whole ingestion run.
        """
        try:
            return self.fetch()
        except Exception as exc:
            print(f"[ingestion] {self.institution} fetch failed: {exc}")
            return []


if __name__ == "__main__":
    # Quick manual test: a fake client that deliberately fails,
    # to confirm safe_fetch() catches it instead of crashing.
    class BrokenClient(SourceClient):
        institution = "TEST-BROKEN"

        def fetch(self):
            raise ConnectionError("simulated network failure")

    class WorkingClient(SourceClient):
        institution = "TEST-WORKING"

        def fetch(self):
            return ["fake record 1", "fake record 2"]

    broken = BrokenClient()
    working = WorkingClient()

    print("Broken client result:", broken.safe_fetch())
    print("Working client result:", working.safe_fetch())
