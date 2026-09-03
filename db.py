# utils/db.py

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "nexera.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            talent_category TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            bio TEXT NOT NULL,
            why_money TEXT NOT NULL,
            image_path TEXT,
            votes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(candidates)").fetchall()}
    if "why_money" not in columns:
        conn.execute("ALTER TABLE candidates ADD COLUMN why_money TEXT DEFAULT ''")
    conn.commit()
    conn.close()
