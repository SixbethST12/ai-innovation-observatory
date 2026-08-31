"""
Source client registry.

FR-1 requires a *configurable* list of approved sources. This file is
that list. Adding a new source means writing one new client file and
adding one import line here - nothing else in the ingestion pipeline
needs to change.
"""

from .bis import BISClient
from .worldbank import WorldBankClient
from .cbk import CBKClient
from .imf import IMFClient

ALL_CLIENTS = [
    BISClient,
    WorldBankClient,
    CBKClient,
    IMFClient,
]
