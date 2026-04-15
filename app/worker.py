import json
from app.redis_client import pop_log, get_queue_depth
from app.db import get_db, init_db
from app.rules import evaluate_rules
from datetime import datetime, timezone


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

def insert_pipeline_metric(recorded_at: str, queue_depth: int, processing_lag_ms: float, logs_processed: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pipeline_metrics (
                recorded_at,
                queue_depth,
                processing_lag_ms,
                logs_processed
            ) VALUES (?, ?, ?, ?)
        """, (
            recorded_at,
            queue_depth,
            processing_lag_ms,
            logs_processed
        ))

def main():
    init_db()
    print("Worker started. Waiting for logs...")

    while True:
        _, raw_event = pop_log()
        event = json.loads(raw_event)
        
        logs_processed = 0

        processed_at = datetime.now(timezone.utc)
        event_time = datetime.fromisoformat(event["timestamp"])
        processing_lag_ms = (processed_at - event_time).total_seconds() * 1000

        print("Processing event:", event)
        process_log(event)
        print("Inserted into database")

        logs_processed += 1
        queue_depth = get_queue_depth()
        
        insert_pipeline_metric(
            recorded_at=processed_at.isoformat(),
            queue_depth=queue_depth,
            processing_lag_ms=processing_lag_ms,
            logs_processed=logs_processed
        )

        alerts = evaluate_rules()

        for alert in alerts:
            print("Alert triggered:", alert)
            insert_alert(alert)

if __name__ == "__main__":
    main()