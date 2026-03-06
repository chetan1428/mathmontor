"""
db_init.py — Database Initialization
Creates the SQLite memory database and tables.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "memory.db"


def init_db():
    """Create the memory database and tables if they don't exist."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text  TEXT NOT NULL,
            input_type  TEXT DEFAULT 'text',
            parsed_json TEXT,
            topic       TEXT,
            answer      TEXT,
            explanation TEXT,
            confidence  INTEGER DEFAULT 0,
            feedback    TEXT DEFAULT '',
            feedback_comment TEXT DEFAULT '',
            rag_sources TEXT DEFAULT '[]',
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ocr_corrections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            original    TEXT,
            corrected   TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
