from datetime import datetime, timedelta, timezone
from app.db import get_db


ERROR_RATE_THRESHOLD = 0.20
LATENCY_THRESHOLD_MS = 500


def get_recent_service_stats(window_seconds: int = 60):
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=window_seconds)).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                service,
                COUNT(*) as log_count,
                SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as error_count,
                AVG(latency_ms) as avg_latency
            FROM logs
            WHERE event_timestamp >= ?
            GROUP BY service
        """, (cutoff,))

        rows = cursor.fetchall()

    stats = []
    for row in rows:
        service, log_count, error_count, avg_latency = row
        error_count = error_count or 0
        avg_latency = avg_latency or 0
        error_rate = error_count / log_count if log_count > 0 else 0

        stats.append({
            "service": service,
            "log_count": log_count,
            "error_count": error_count,
            "error_rate": error_rate,
            "avg_latency": avg_latency
        })

    return stats


def evaluate_rules(window_seconds: int = 60):
    stats = get_recent_service_stats(window_seconds=window_seconds)
    alerts = []

    for stat in stats:
        service = stat["service"]

        if stat["error_rate"] > ERROR_RATE_THRESHOLD:
            alerts.append({
                "service": service,
                "alert_type": "HIGH_ERROR_RATE",
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "value": stat["error_rate"],
                "threshold": ERROR_RATE_THRESHOLD,
                "message": f"{service} error rate {stat['error_rate']:.2f} exceeded threshold {ERROR_RATE_THRESHOLD:.2f}"
            })

        if stat["avg_latency"] > LATENCY_THRESHOLD_MS:
            alerts.append({
                "service": service,
                "alert_type": "HIGH_LATENCY",
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "value": stat["avg_latency"],
                "threshold": LATENCY_THRESHOLD_MS,
                "message": f"{service} avg latency {stat['avg_latency']:.2f}ms exceeded threshold {LATENCY_THRESHOLD_MS}ms"
            })

    return alerts