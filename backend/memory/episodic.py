"""
SQLite episodic memory — stores query/response history locally.
"""

import sqlite3
import json
import os
from datetime import datetime


_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "memory.db")


def _conn():
    db = sqlite3.connect(_DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            summary TEXT,
            root_cause TEXT,
            confidence REAL
        )
    """)
    db.commit()
    return db


def save_episode(question: str, summary: str, root_cause: str, confidence: float):
    db = _conn()
    db.execute(
        "INSERT INTO episodes (timestamp, question, summary, root_cause, confidence) VALUES (?,?,?,?,?)",
        (datetime.utcnow().isoformat(), question, summary, root_cause, confidence)
    )
    db.commit()
    db.close()


def recent_episodes(limit: int = 5) -> list:
    db = _conn()
    rows = db.execute(
        "SELECT timestamp, question, summary, root_cause, confidence FROM episodes ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    db.close()
    return [
        {"timestamp": r[0], "question": r[1], "summary": r[2], "root_cause": r[3], "confidence": r[4]}
        for r in rows
    ]
