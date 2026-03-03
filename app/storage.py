import os
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parent.parent / "urls.db")))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                short_code TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def save_link(short_code: str, original_url: str) -> bool:
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO links (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url),
            )
            connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_original_url(short_code: str) -> Optional[str]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT original_url FROM links WHERE short_code = ?",
            (short_code,),
        ).fetchone()
    return row["original_url"] if row else None


def short_code_exists(short_code: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM links WHERE short_code = ?",
            (short_code,),
        ).fetchone()
    return row is not None
