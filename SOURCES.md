# Source Verification Log

Tracks how each data source in the ingestion layer was verified, and
why sources that were considered but not implemented were excluded.
Kept so decisions don't need to be re-discovered later.

## Implemented sources

| Source | Access method | Verified | Notes |
|---|---|---|---|
| BIS | RSS (`data.bis.org/feed.xml`) | Yes - 113 records | Original publications feed (`bis.org/doclist/*.rss`) went dead mid-project (site restructured ~2026-08-31, confirmed via curl - BIS's own server returns a real 404). Switched to their statistics release calendar feed instead. Same link can repeat across multiple pubDates (weekly re-releases) - dedup correctly collapses these to one stored record per release type. |
| World Bank | REST API (`search.worldbank.org/api/v3/wds`) | Yes - real documents returned | `documents` response object contains a non-document `facets` key that must be explicitly skipped. No documented `order` parameter exists - not used. |
| Central Bank of Kenya (CBK) | RSS (`centralbank.go.ke/feed/`) | Yes - 10 records | No advertised RSS/API. Site runs on WordPress; default `/feed/` endpoint works even though it isn't linked anywhere on the site. |
| IMF | REST API (`api.imf.org/external/sdmx/3.0/...`) | Yes - 20 countries, real CPI data | No working publications RSS found (site is JS-rendered, old feed URLs are dead). Uses IMF's SDMX statistical data API instead - genuinely different data type (economic indicators, not documents). One record built per country rather than per document, since this is time-series data. |

## Considered but not implemented

| Source | Reason not implemented |
|---|---|
| National Bank of Rwanda (BNR) | No RSS feed or public API found. Site (`bnr.rw`) is a JavaScript-rendered single-page app - confirmed via direct fetch (returns only "You need to enable JavaScript to run this app", no static content). No feed auto-discovery possible the way it was for CBK (WordPress). Could potentially be reached via browser DevTools Network tab to find an internal API the JS app calls, but this was not pursued. |
| BIS SDMX statistical API (`stats.bis.org/api`) | Real, documented, separate from the RSS feed already implemented. Not pursued because it provides numeric statistical data rather than publications, and Tanzania's data coverage in this specific API could not be confirmed. Documented here as a possible future extension. |

## Design notes

- Every RSS/API URL in this project was verified with a real request
  (curl, browser DevTools, or a direct test run) before being written
  into a client - none were used purely on documentation or assumption.
- Two sources (BIS, IMF) required real debugging during this project:
  BIS's original feed URL died mid-project due to a site restructure;
  IMF required distinguishing between a dead RSS feed and a working
  but differently-purposed SDMX API.

## Data quality caveat: BIS published_date semantics (found 2026-09-03)

BIS's `data.bis.org/feed.xml` (used by `bis.py`) is explicitly a
**"release calendar"** feed, confirmed directly from its own
description: *"Find here the latest publication dates of BIS
statistics. Data are released no later than the specified date."*

This means `published_date` for BIS records can be a **scheduled
future release date**, not a "this already happened" date - unlike
every other source (World Bank, CBK, IMF), where published_date
reflects something that has actually occurred.

Found while reviewing real trend detection output: a trend window of
"2026-11" appeared in results computed on 2026-09-03 - a future date,
traced back to this feed's actual semantics rather than a bug in
`trend_engine.py`.

Impact: trend detection (FR-9/FR-10) treats all sources' published_date
uniformly. For BIS specifically, an apparent "spike" could partly
reflect scheduled future releases rather than genuine recent
publishing activity. Not fixed in this phase - documented so it isn't
mistaken for a bug, and so any analyst using the Trends view knows to
interpret BIS-sourced trend spikes with this caveat in mind.
