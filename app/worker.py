import json
from app.redis_client import pop_log
from app.db import get_db, init_db
from app.rules import evaluate_rules


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

def insert_alert(alert: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (
                service,
                alert_type,
                triggered_at,
                value,
                threshold,
                message
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert["service"],
            alert["alert_type"],
            alert["triggered_at"],
            alert["value"],
            alert["threshold"],
            alert["message"]
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

        alerts = evaluate_rules()

        for alert in alerts:
            print("Alert triggered:", alert)
            insert_alert(alert)

if __name__ == "__main__":
    main()

