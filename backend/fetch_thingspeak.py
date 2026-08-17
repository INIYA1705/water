"""Fetch readings from ThingSpeak and store locally."""

import os
from datetime import datetime

import requests

import config  # noqa: F401 — loads .env from project root
from database import init_db, insert_reading, insert_alert

CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID")
READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY")
RESULTS_COUNT = int(os.getenv("FETCH_RESULTS_COUNT", "100"))


def fetch_feeds() -> list[dict]:
    if not CHANNEL_ID or not READ_API_KEY:
        raise ValueError("Set THINGSPEAK_CHANNEL_ID and THINGSPEAK_READ_API_KEY in .env")

    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
    params = {"api_key": READ_API_KEY, "results": RESULTS_COUNT}

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json().get("feeds", [])


def parse_feed(feed: dict) -> tuple:
    entry_id = int(feed["entry_id"])
    created_at = feed["created_at"]
    fields = [
        feed.get(f"field{i}") for i in range(1, 7)
    ]
    parsed = []
    for val in fields:
        if val is None or val == "":
            parsed.append(None)
        else:
            try:
                parsed.append(float(val))
            except ValueError:
                parsed.append(val)
    return entry_id, created_at, parsed


def sync_from_thingspeak() -> int:
    init_db()
    feeds = fetch_feeds()
    new_count = 0

    for feed in feeds:
        entry_id, created_at, fields = parse_feed(feed)
        insert_reading(entry_id, created_at, *fields)
        new_count += 1

        leak = fields[3]
        ph = fields[4]
        turbidity = fields[5]

        if leak == 1:
            insert_alert(
                "leak",
                f"Leak detected at {created_at}. Check pipes and valves.",
                "critical",
            )
        if ph is not None and (ph < 6.5 or ph > 8.5):
            insert_alert(
                "quality",
                f"pH out of safe range: {ph} (safe: 6.5–8.5)",
                "warning",
            )
        if turbidity is not None and turbidity > 5:
            insert_alert(
                "quality",
                f"High turbidity: {turbidity} NTU (safe: < 5 NTU)",
                "warning",
            )

    return new_count


if __name__ == "__main__":
    count = sync_from_thingspeak()
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Synced {count} readings from ThingSpeak")
