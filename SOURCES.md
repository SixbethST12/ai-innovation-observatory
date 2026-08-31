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
