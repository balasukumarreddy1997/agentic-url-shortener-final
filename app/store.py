import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = os.getenv("DATABASE_PATH", "./url_shortener.db")


<<<<<<< HEAD
class DuplicateCode(Exception):
    """The short code violates the primary-key uniqueness constraint."""


=======
>>>>>>> origin/main
class SQLiteStore:
    """Small persistence adapter. Each operation owns its connection for thread safety."""

    def __init__(self, path: str | None = None):
        self.path = path or DEFAULT_DB

    def _connect(self):
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    code TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    clicks INTEGER NOT NULL DEFAULT 0,
                    last_clicked_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS click_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL REFERENCES urls(code) ON DELETE CASCADE,
                    clicked_at TEXT NOT NULL,
                    user_agent TEXT,
                    referrer TEXT
                )
            """)

    def get_url(self, code: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM urls WHERE code = ?", (code,)).fetchone()
            return dict(row) if row else None

    def insert_url(self, code: str, original_url: str, created_at: str):
<<<<<<< HEAD
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO urls(code, original_url, created_at) VALUES (?, ?, ?)",
                    (code, original_url, created_at),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateCode(code) from exc
=======
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO urls(code, original_url, created_at) VALUES (?, ?, ?)",
                (code, original_url, created_at),
            )
>>>>>>> origin/main

    def record_click(
        self, code: str, clicked_at: str, user_agent: str | None, referrer: str | None
    ):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO click_events(code, clicked_at, user_agent, referrer) VALUES (?, ?, ?, ?)",
                (code, clicked_at, user_agent, referrer),
            )
            conn.execute(
                "UPDATE urls SET clicks = clicks + 1, last_clicked_at = ? WHERE code = ?",
                (clicked_at, code),
            )
