"""
Scheduler.

TEMPORARY: INGESTION_PAUSED = True below - stops pulling new records
so the AI processing backlog can catch up (IMF alone adds ~40/day,
outpacing AI processing capacity). AI processing and trend
computation keep running normally. Set back to False to resume
normal ingestion once the backlog clears.
"""

from apscheduler.schedulers.blocking import BlockingScheduler

try:
    from .pipeline import run_ingestion, store_records
    from ..ai.processor import process_batch
    from ..ai.llm_client import OllamaNotRunningError
    from ..trends.trend_engine import compute_trends, save_trends
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ingestion.pipeline import run_ingestion, store_records
    from ai.processor import process_batch
    from ai.llm_client import OllamaNotRunningError
    from trends.trend_engine import compute_trends, save_trends

INTERVAL_SECONDS = 21600  # 6 hours
AI_BATCH_PER_CYCLE = 50   # raised from 30, since we're not spending cycle time on ingestion right now
INGESTION_PAUSED = True   # <-- set back to False to resume normal ingestion


def scheduled_job():
    if INGESTION_PAUSED:
        print("\n[scheduler] Ingestion PAUSED - skipping fetch/store, clearing AI backlog instead")
    else:
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

    print("\n[scheduler] Recomputing trends...")
    try:
        trends_df = compute_trends()
        if not trends_df.empty:
            saved_trends = save_trends(trends_df)
            emerging_count = int(trends_df["is_emerging"].sum())
            print(f"[scheduler] Trends updated: {saved_trends} record(s), {emerging_count} emerging")
        else:
            print("[scheduler] No trend data available yet")
    except Exception as e:
        print(f"[scheduler] Trend computation failed: {e}")

    print("[scheduler] Job complete.\n")


if __name__ == "__main__":
    print(f"[scheduler] Starting - job will run every {INTERVAL_SECONDS} seconds")
    print(f"[scheduler] Ingestion paused: {INGESTION_PAUSED}")
    print(f"[scheduler] AI processing: up to {AI_BATCH_PER_CYCLE} records per cycle")
    print("[scheduler] Press Ctrl+C to stop\n")

    scheduled_job()

    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, "interval", seconds=INTERVAL_SECONDS)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[scheduler] Stopped by user")
