import json
from app.redis_client import pop_log
from app.db import get_db, init_db


def process_log(event: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (
                event_timestamp,
                ingested_at,
                service,
                host,
                level,
                message,
                latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event["timestamp"],
            event["ingested_at"],
            event["service"],
            event["host"],
            event["level"],
            event["message"],
            event["latency_ms"]
        ))


def main():
    init_db()
    print("Worker started. Waiting for logs...")

    while True:
        _, raw_event = pop_log()
        event = json.loads(raw_event)
        print("Processing event:", event)
        process_log(event)
        print("Inserted into database")


if __name__ == "__main__":
    main()