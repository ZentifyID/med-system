"""Единая точка подключения к базе данных.

При переходе на PostgreSQL нужно будет изменить только этот модуль
(и плейсхолдеры ? -> %s в запросах).
"""
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.config import DB_PATH


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Контекстный менеджер: открывает соединение, включает foreign keys,
    коммитит при успехе, откатывает при ошибке, всегда закрывает."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
