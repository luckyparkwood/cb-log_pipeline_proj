import sqlite3
from contextlib import contextmanager

DB_NAME = "logs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_timestamp TEXT,
        ingested_at TEXT,
        service TEXT,
        host TEXT,
        level TEXT,
        message TEXT,
        latency_ms INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        alert_type TEXT,
        triggered_at TEXT,
        value REAL,
        threshold REAL,
        message TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recorded_at TEXT,
        queue_depth INTEGER,
        processing_lag_ms REAL,
        logs_processed INTEGER
    )
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()