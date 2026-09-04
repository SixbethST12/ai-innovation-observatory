"""
Trend detection - FR-9, FR-10.

Counts how often each topic appears per month (using published_date,
NOT fetched_at - published_date reflects when content was actually
published, fetched_at just reflects when our ingestion happened to
run, which would produce a fake "everything is trending now" result).

A topic is flagged "emerging" if its most recent month's count is
at least 1.5x the average of all prior months for that topic - a
simple, explainable threshold rather than a complex statistical model,
appropriate for this project's scope.
"""

import pandas as pd
from datetime import datetime

try:
    from ..db.database import get_session, engine, Base
    from ..db.db_models import Publication, Trend
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db.database import get_session, engine, Base
    from db.db_models import Publication, Trend

EMERGING_THRESHOLD = 1.5  # recent month must be 1.5x the prior average to flag as emerging


def load_topic_data() -> pd.DataFrame:
    """
    Pulls all publications with a topic and a published_date, explodes
    multi-topic rows into one row per topic, returns a clean DataFrame
    with columns: topic, month (YYYY-MM string).
    """
    session = get_session()
    try:
        records = session.query(Publication.topics, Publication.published_date).filter(
            Publication.topics.isnot(None),
            Publication.topics != "",
            Publication.published_date.isnot(None),
        ).all()
    finally:
        session.close()

    if not records:
        return pd.DataFrame(columns=["topic", "month"])

    df = pd.DataFrame(records, columns=["topics", "published_date"])

    # Split "Monetary Policy, Financial Stability" into separate rows
    df["topic"] = df["topics"].str.split(",")
    df = df.explode("topic")
    df["topic"] = df["topic"].str.strip()
    df = df[df["topic"] != ""]

    df["month"] = pd.to_datetime(df["published_date"]).dt.strftime("%Y-%m")

    return df[["topic", "month"]]


def compute_trends() -> pd.DataFrame:
    """
    Groups by topic + month, counts publications, flags emerging
    topics. Returns a DataFrame ready to be saved to the trends table.
    """
    df = load_topic_data()
    if df.empty:
        print("[trends] No topic data available yet - process more records first.")
        return pd.DataFrame()

    counts = df.groupby(["topic", "month"]).size().reset_index(name="publication_count")
    counts = counts.sort_values(["topic", "month"])

    results = []
    for topic in counts["topic"].unique():
        topic_data = counts[counts["topic"] == topic].sort_values("month")

        if len(topic_data) < 2:
            # Only one month of data - nothing to compare against yet
            row = topic_data.iloc[-1]
            results.append({
                "topic": topic,
                "time_window": row["month"],
                "publication_count": int(row["publication_count"]),
                "is_emerging": False,
            })
            continue

        latest = topic_data.iloc[-1]
        prior_months = topic_data.iloc[:-1]
        prior_avg = prior_months["publication_count"].mean()

        is_emerging = latest["publication_count"] >= (prior_avg * EMERGING_THRESHOLD)

        results.append({
            "topic": topic,
            "time_window": latest["month"],
            "publication_count": int(latest["publication_count"]),
            "is_emerging": bool(is_emerging),
        })

    return pd.DataFrame(results)


def save_trends(trends_df: pd.DataFrame) -> int:
    """Saves computed trends to the trends table. Returns count saved."""
    if trends_df.empty:
        return 0

    Base.metadata.create_all(engine)
    session = get_session()
    saved = 0
    try:
        for _, row in trends_df.iterrows():
            trend = Trend(
                topic=row["topic"],
                time_window=row["time_window"],
                publication_count=row["publication_count"],
                is_emerging=row["is_emerging"],
                computed_at=datetime.utcnow(),
            )
            session.add(trend)
            saved += 1
        session.commit()
    finally:
        session.close()
    return saved


if __name__ == "__main__":
    print("Computing trends from real stored publications...\n")
    trends_df = compute_trends()

    if trends_df.empty:
        print("No trends computed.")
    else:
        print(trends_df.to_string(index=False))
        saved = save_trends(trends_df)
        print(f"\nSaved {saved} trend record(s) to database.")

        emerging = trends_df[trends_df["is_emerging"] == True]
        if not emerging.empty:
            print(f"\n{len(emerging)} EMERGING TOPIC(S) DETECTED:")
            for _, row in emerging.iterrows():
                print(f"  - {row['topic']} ({row['time_window']}): {row['publication_count']} publications")
