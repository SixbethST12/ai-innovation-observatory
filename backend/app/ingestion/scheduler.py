"""
Scheduler.

Automates the full pipeline on one timer:
  1. Ingestion: fetch -> normalize -> dedup -> store (FR-2)
  2. AI processing: summarize -> classify -> relevance (FR-5, FR-7,
     FR-8, FR-11) for a batch of unprocessed records

AI batch is capped per cycle (30, not "all unprocessed at once") so
one scheduler cycle doesn't run for an hour straight - remaining
records get picked up gradually across subsequent cycles instead.

IMPORTANT OPERATIONAL NOTE: Ollama must be running (`ollama serve`)
for the AI step to work. If it isn't, AI processing is skipped for
that cycle (logged clearly) but ingestion still completes normally -
one failing stage doesn't block the other, same failure-isolation
principle as base_client.py's safe_fetch().
"""

from apscheduler.schedulers.blocking import BlockingScheduler

try:
    from .pipeline import run_ingestion, store_records
    from ..ai.processor import process_batch
    from ..ai.llm_client import OllamaNotRunningError
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ingestion.pipeline import run_ingestion, store_records
    from ai.processor import process_batch
    from ai.llm_client import OllamaNotRunningError

INTERVAL_SECONDS = 21600  # 6 hours - production interval
AI_BATCH_PER_CYCLE = 30   # process up to 30 records per cycle, not all at once


def scheduled_job():
    print("\n" + "=" * 50)
    print("[scheduler] Running ingestion job...")
    print("=" * 50)
    records = run_ingestion()
    saved = store_records(records)
    print(f"[scheduler] Ingestion complete: {saved} new record(s) saved, "
          f"{len(records) - saved} already existed")

    print(f"\n[scheduler] Running AI processing job (up to {AI_BATCH_PER_CYCLE} records)...")
    try:
        process_batch(limit=AI_BATCH_PER_CYCLE)
    except OllamaNotRunningError as e:
        print(f"[scheduler] AI processing skipped - {e}")

    print("[scheduler] Job complete.\n")


if __name__ == "__main__":
    print(f"[scheduler] Starting - job will run every {INTERVAL_SECONDS} seconds")
    print(f"[scheduler] AI processing: up to {AI_BATCH_PER_CYCLE} records per cycle")
    print("[scheduler] NOTE: Ollama must be running (ollama serve) for AI processing to work")
    print("[scheduler] Press Ctrl+C to stop\n")

    scheduled_job()

    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, "interval", seconds=INTERVAL_SECONDS)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[scheduler] Stopped by user")
