from datetime import datetime, timedelta, timezone
import time
from app.db import get_db


def get_totals():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]

    return total_logs, total_alerts


def get_recent_service_stats(window_seconds=60):
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=window_seconds)).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                service,
                COUNT(*) as log_count,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as error_count
            FROM logs
            WHERE event_timestamp >= ?
            GROUP BY service
        """, (cutoff,))

        return cursor.fetchall()


def get_recent_alerts(limit=10):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT service, alert_type, value, threshold, triggered_at
            FROM alerts
            ORDER BY triggered_at DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

def get_pipeline_health():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT recorded_at, queue_depth, processing_lag_ms, logs_processed
            FROM pipeline_metrics
            ORDER BY id DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()

        cursor.execute("""
            SELECT AVG(processing_lag_ms)
            FROM pipeline_metrics
            ORDER BY id DESC
            LIMIT 20
        """)
        avg_lag_row = cursor.fetchone()

    avg_lag = avg_lag_row[0] if avg_lag_row and avg_lag_row[0] is not None else 0
    return latest, avg_lag

def get_processing_rate(window_seconds=60):
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=window_seconds)).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM pipeline_metrics
            WHERE recorded_at >= ?
        """, (cutoff,))
        count = cursor.fetchone()[0]

    return count / window_seconds

def main():
    print("\n=== Pipeline Report ===\n")

    total_logs, total_alerts = get_totals()
    print(f"Total logs: {total_logs}")
    print(f"Total alerts: {total_alerts}")

    latest_metric, avg_lag = get_pipeline_health()
    processing_rate = get_processing_rate()

    print("\n--- Pipeline Health ---")
    if latest_metric:
        recorded_at, queue_depth, processing_lag_ms, logs_processed = latest_metric
        print(f"Latest queue depth: {queue_depth}")
        print(f"Latest processing lag: {processing_lag_ms:.2f} ms")
        print(f"Logs processed by worker: {logs_processed}")
        print(f"Average processing lag (recent): {avg_lag:.2f} ms")
        print(f"Approx processing rate: {processing_rate:.2f} logs/sec")
    else:
        print("No pipeline metrics recorded yet.")

    print("\n--- Recent Service Stats (last 60s) ---")
    stats = get_recent_service_stats()

    for row in stats:
        service, log_count, avg_latency, error_count = row
        error_rate = (error_count or 0) / log_count if log_count else 0

        print(
            f"{service}: logs={log_count}, "
            f"avg_latency={avg_latency:.1f}ms, "
            f"errors={error_count}, "
            f"error_rate={error_rate:.2f}"
        )

    print("\n--- Recent Alerts ---")
    alerts = get_recent_alerts()

    for row in alerts:
        service, alert_type, value, threshold, triggered_at = row
        print(
            f"{triggered_at} | {service} | {alert_type} "
            f"value={value:.2f} threshold={threshold}"
        )

    print("\n=====================\n")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(5)