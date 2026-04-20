import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "med_system.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                affiliation TEXT NOT NULL CHECK(affiliation IN ('основной', 'внешний')),
                passport_series TEXT NOT NULL,
                passport_number TEXT NOT NULL,
                passport_issued_by TEXT NOT NULL,
                passport_issue_date TEXT NOT NULL,
                passport_department_code TEXT NOT NULL,
                oms TEXT NOT NULL,
                address TEXT NOT NULL,
                sanminimum_date TEXT NOT NULL,
                medical_exam_date TEXT NOT NULL,
                fluorography_date TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def fetch_employees_for_table() -> list[tuple[str, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT
                last_name || ' ' || first_name || ' ' || middle_name AS fio,
                affiliation
            FROM employees
            ORDER BY last_name, first_name, middle_name
            """
        ).fetchall()
        result: list[tuple[str, str]] = []
        for fio, affiliation in rows:
            label = "внешний совместитель" if affiliation == "внешний" else affiliation
            result.append((str(fio), str(label)))
        return result
    finally:
        conn.close()


def insert_employee(data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO employees (
                last_name,
                first_name,
                middle_name,
                birth_date,
                affiliation,
                passport_series,
                passport_number,
                passport_issued_by,
                passport_issue_date,
                passport_department_code,
                oms,
                address,
                sanminimum_date,
                medical_exam_date,
                fluorography_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["last_name"],
                data["first_name"],
                data["middle_name"],
                data["birth_date"],
                data["affiliation"],
                data["passport_series"],
                data["passport_number"],
                data["passport_issued_by"],
                data["passport_issue_date"],
                data["passport_department_code"],
                data["oms"],
                data["address"],
                data["sanminimum_date"],
                data["medical_exam_date"],
                data["fluorography_date"],
            ),
        )
        conn.commit()
    finally:
        conn.close()
