import sqlite3
from contextlib import contextmanager

DB_NAME = "logs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # logs table
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

    # alerts table
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

    conn.commit()
    conn.close()


#connection helper
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()