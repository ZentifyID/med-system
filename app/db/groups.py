"""Работа с учебными группами."""
import sqlite3
from datetime import datetime

from app.config import ACADEMIC_YEAR_ROLLOVER
from app.db.connection import get_connection


def fetch_groups() -> list[tuple[int, str]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name FROM groups ORDER BY name").fetchall()
    return [(int(id), str(name)) for id, name in rows]


def fetch_group_by_id(group_id: int) -> dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name FROM groups WHERE id = ?", (group_id,)
        ).fetchone()
    if not row:
        return None
    return {"id": str(row[0]), "name": str(row[1])}


def get_student_count_by_group(group_id: int) -> int:
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM students WHERE group_id = ?", (group_id,)
        ).fetchone()[0]
    return int(count)


def insert_group(name: str) -> None:
    with get_connection() as conn:
        conn.execute("INSERT INTO groups (name) VALUES (?)", (name,))


def update_group(group_id: int, name: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE groups SET name = ? WHERE id = ?", (name, group_id))


def delete_group(group_id: int, cascade: bool = False) -> None:
    """Удаляет группу. При cascade=True сначала удаляет студентов группы.
    Обе операции выполняются в одной транзакции."""
    with get_connection() as conn:
        if cascade:
            conn.execute("DELETE FROM students WHERE group_id = ?", (group_id,))
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))


def _increment_groups(conn: sqlite3.Connection) -> int:
    """Увеличивает первую цифру в названиях групп (11-А -> 21-А).
    Работает внутри переданной транзакции."""
    rows = conn.execute("SELECT id, name FROM groups").fetchall()
    to_update = []
    for gid, name in rows:
        if name and name[0].isdigit():
            first_digit = int(name[0])
            new_name = str(first_digit + 1) + name[1:]
            if new_name != name:
                to_update.append((gid, name, new_name, first_digit))

    # Сортировка по убыванию первой цифры, чтобы избежать конфликтов UNIQUE
    to_update.sort(key=lambda x: x[3], reverse=True)

    count = 0
    for gid, old_name, new_name, _ in to_update:
        try:
            conn.execute("UPDATE groups SET name = ? WHERE id = ?", (new_name, gid))
            count += 1
        except sqlite3.IntegrityError:
            raise Exception(
                f"Не удалось перевести группу '{old_name}', "
                f"так как группа '{new_name}' уже существует."
            )
    return count


def increment_first_digit_in_all_groups() -> int:
    with get_connection() as conn:
        return _increment_groups(conn)


def check_and_auto_increment_groups() -> int:
    """После даты начала учебного года (по умолчанию 15 августа) один раз в год
    автоматически переводит группы на следующий курс.
    Проверка и перевод выполняются в одной транзакции."""
    now = datetime.now()
    month, day = ACADEMIC_YEAR_ROLLOVER
    if now.month < month or (now.month == month and now.day < day):
        return 0

    current_year = str(now.year)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM system_info WHERE key = 'last_group_increment_year'"
        ).fetchone()
        last_year = row[0] if row else None
        if last_year == current_year:
            return 0

        count = _increment_groups(conn)
        conn.execute(
            "INSERT OR REPLACE INTO system_info (key, value) VALUES ('last_group_increment_year', ?)",
            (current_year,),
        )
        return count
