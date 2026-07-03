"""Работа со студентами."""
from app.db.connection import get_connection

STUDENT_COLUMNS = [
    "id",
    "group_id",
    "last_name",
    "first_name",
    "middle_name",
    "birth_date",
    "oms",
    "address",
    "sanminimum_date",
    "medical_exam_date",
    "fluorography_date",
]

_DATA_COLUMNS = STUDENT_COLUMNS[1:]  # все, кроме id


def fetch_students_for_table() -> list[tuple[int, str, str, str, str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.id,
                s.last_name || ' ' || s.first_name || ' ' || s.middle_name AS fio,
                g.name AS group_name,
                s.sanminimum_date,
                s.medical_exam_date,
                s.fluorography_date
            FROM students s
            JOIN groups g ON s.group_id = g.id
            ORDER BY s.last_name, s.first_name, s.middle_name
            """
        ).fetchall()
    return [
        (int(id), str(fio), str(group_name), str(san), str(med), str(flu))
        for id, fio, group_name, san, med, flu in rows
    ]


def fetch_student_by_id(student_id: int) -> dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {', '.join(STUDENT_COLUMNS)} FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()
    if not row:
        return None
    return {col: str(value) for col, value in zip(STUDENT_COLUMNS, row)}


def insert_student(data: dict[str, str]) -> None:
    placeholders = ", ".join("?" for _ in _DATA_COLUMNS)
    with get_connection() as conn:
        conn.execute(
            f"INSERT INTO students ({', '.join(_DATA_COLUMNS)}) VALUES ({placeholders})",
            tuple(data[col] for col in _DATA_COLUMNS),
        )


def update_student(student_id: int, data: dict[str, str]) -> None:
    assignments = ", ".join(f"{col} = ?" for col in _DATA_COLUMNS)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE students SET {assignments} WHERE id = ?",
            tuple(data[col] for col in _DATA_COLUMNS) + (student_id,),
        )


def delete_student(student_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
