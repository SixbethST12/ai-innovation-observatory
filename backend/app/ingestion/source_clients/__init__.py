"""
Source client registry.

FR-1 requires a *configurable* list of approved sources. This file is
that list. Adding a new source (another peer central bank, for
example) means writing one new client file and adding one import line
here — nothing else in the ingestion pipeline needs to change.

IMF is deliberately NOT included yet: no confirmed working RSS feed
URL has been found for it (their site is JavaScript-rendered and the
old feed URLs appear dead). Add it once a real URL is confirmed.
"""

from .bis import BISClient
from .worldbank import WorldBankClient
from .cbk import CBKClient

ALL_CLIENTS = [
    BISClient,
    WorldBankClient,
    CBKClient,
    # IMFClient,  # paused - no confirmed RSS feed URL yet
]
