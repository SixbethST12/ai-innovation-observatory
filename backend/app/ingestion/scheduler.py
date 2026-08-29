"""
Scheduler.

Automates pipeline.py so ingestion runs on a timer instead of
requiring someone to run `python3 pipeline.py` manually. Satisfies
FR-2 (retrieve new publications on a scheduled basis).

Uses APScheduler (a Python library) rather than OS-level cron, since
cron needs configuration outside this codebase and isn't reliable
inside a Codespace by default. APScheduler keeps scheduling as part
of the application itself.

TESTING interval is 30 seconds so you can watch it fire multiple
times quickly. Change INTERVAL_SECONDS to something like 21600
(6 hours) before real deployment - hitting BIS/World Bank/CBK every
30 seconds in production would be excessive and could get you
rate-limited or blocked.
"""

from apscheduler.schedulers.blocking import BlockingScheduler

try:
    from .pipeline import run_ingestion, store_records
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pipeline import run_ingestion, store_records

INTERVAL_SECONDS = 21600  # 6 hours - production interval


def scheduled_job():
    print("\n" + "=" * 50)
    print("[scheduler] Running ingestion job...")
    print("=" * 50)
    records = run_ingestion()
    saved = store_records(records)
    print(f"[scheduler] Job complete: {saved} new record(s) saved, "
          f"{len(records) - saved} already existed")


if __name__ == "__main__":
    print(f"[scheduler] Starting - job will run every {INTERVAL_SECONDS} seconds")
    print("[scheduler] Press Ctrl+C to stop\n")

    # Run once immediately so you don't wait for the first interval
    scheduled_job()

    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, "interval", seconds=INTERVAL_SECONDS)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[scheduler] Stopped by user")
