"""Database setup and models for water consumption readings."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "water_consumption.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER UNIQUE,
            created_at TEXT NOT NULL,
            water_consumption REAL,
            flow_rate REAL,
            water_pressure REAL,
            leak_status INTEGER,
            ph REAL,
            turbidity REAL
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'warning'
        );

        CREATE INDEX IF NOT EXISTS idx_readings_created ON readings(created_at);
    """)
    conn.commit()
    conn.close()


def insert_reading(entry_id, created_at, field1, field2, field3, field4, field5, field6):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR IGNORE INTO readings
        (entry_id, created_at, water_consumption, flow_rate, water_pressure,
         leak_status, ph, turbidity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (entry_id, created_at, field1, field2, field3, field4, field5, field6),
    )
    conn.commit()
    conn.close()


def insert_alert(alert_type: str, message: str, severity: str = "warning"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO alerts (created_at, alert_type, message, severity) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), alert_type, message, severity),
    )
    conn.commit()
    conn.close()


def get_recent_readings(limit: int = 100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM readings ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_readings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM readings ORDER BY created_at ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_alerts(limit: int = 20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
