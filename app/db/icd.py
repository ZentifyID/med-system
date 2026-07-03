"""Справочник кодов МКБ."""
import sqlite3

from app.db.connection import get_connection


def _register_lower(conn: sqlite3.Connection) -> None:
    # Встроенный LOWER в SQLite не работает с кириллицей,
    # поэтому регистрируем функцию на Python
    conn.create_function("py_lower", 1, lambda s: s.lower() if s else "")


def search_icd_codes(query: str) -> list[dict]:
    with get_connection() as conn:
        _register_lower(conn)
        q = f"%{query.lower()}%"
        rows = conn.execute(
            """
            SELECT code, name FROM icd_codes
            WHERE py_lower(code) LIKE ? OR py_lower(name) LIKE ?
            ORDER BY code LIMIT 30
            """,
            (q, q),
        ).fetchall()
    return [{"code": r[0], "name": r[1]} for r in rows]


def fetch_all_icd_codes(query: str = "") -> list[dict]:
    with get_connection() as conn:
        _register_lower(conn)
        if query:
            q = f"%{query.lower()}%"
            rows = conn.execute(
                """
                SELECT code, name FROM icd_codes
                WHERE py_lower(code) LIKE ? OR py_lower(name) LIKE ?
                ORDER BY code
                """,
                (q, q),
            ).fetchall()
        else:
            rows = conn.execute("SELECT code, name FROM icd_codes ORDER BY code").fetchall()
    return [{"code": r[0], "name": r[1]} for r in rows]


def insert_icd_code(code: str, name: str) -> bool:
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO icd_codes (code, name) VALUES (?, ?)", (code, name))
        return True
    except sqlite3.IntegrityError:
        return False


def update_icd_code(old_code: str, new_code: str, new_name: str) -> bool:
    try:
        with get_connection() as conn:
            if old_code != new_code:
                row = conn.execute(
                    "SELECT 1 FROM icd_codes WHERE code = ?", (new_code,)
                ).fetchone()
                if row:
                    return False
            conn.execute(
                "UPDATE icd_codes SET code = ?, name = ? WHERE code = ?",
                (new_code, new_name, old_code),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def delete_icd_code(code: str) -> bool:
    with get_connection() as conn:
        conn.execute("DELETE FROM icd_codes WHERE code = ?", (code,))
    return True
