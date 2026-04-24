import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "med_system.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                passport_series TEXT NOT NULL,
                passport_number TEXT NOT NULL,
                passport_issued_by TEXT NOT NULL,
                passport_issue_date TEXT NOT NULL,
                passport_department_code TEXT NOT NULL,
                oms TEXT NOT NULL,
                address TEXT NOT NULL,
                sanminimum_date TEXT NOT NULL,
                medical_exam_date TEXT NOT NULL,
                fluorography_date TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                expiration_date TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appeals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                sender TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def fetch_employees_for_table() -> list[tuple[int, str, str, str, str, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT
                id,
                last_name || ' ' || first_name || ' ' || middle_name AS fio,
                affiliation,
                sanminimum_date,
                medical_exam_date,
                fluorography_date
            FROM employees
            ORDER BY last_name, first_name, middle_name
            """
        ).fetchall()
        result: list[tuple[int, str, str, str, str, str]] = []
        for id, fio, affiliation, san_date, med_date, flu_date in rows:
            label = "внешний совместитель" if affiliation == "внешний" else affiliation
            result.append((int(id), str(fio), str(label), str(san_date), str(med_date), str(flu_date)))
        return result
    finally:
        conn.close()


def fetch_employee_by_id(employee_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()
        if not row:
            return None

        keys = [
            "id",
            "last_name",
            "first_name",
            "middle_name",
            "birth_date",
            "affiliation",
            "passport_series",
            "passport_number",
            "passport_issued_by",
            "passport_issue_date",
            "passport_department_code",
            "oms",
            "address",
            "sanminimum_date",
            "medical_exam_date",
            "fluorography_date",
        ]
        return {keys[i]: str(value) for i, value in enumerate(row)}
    finally:
        conn.close()


def update_employee(employee_id: int, data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            UPDATE employees
            SET
                last_name = ?,
                first_name = ?,
                middle_name = ?,
                birth_date = ?,
                affiliation = ?,
                passport_series = ?,
                passport_number = ?,
                passport_issued_by = ?,
                passport_issue_date = ?,
                passport_department_code = ?,
                oms = ?,
                address = ?,
                sanminimum_date = ?,
                medical_exam_date = ?,
                fluorography_date = ?
            WHERE id = ?
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
                employee_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_employee(employee_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
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


def fetch_groups() -> list[tuple[int, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT id, name FROM groups ORDER BY name").fetchall()
        return [(int(id), str(name)) for id, name in rows]
    finally:
        conn.close()


def fetch_group_by_id(group_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT id, name FROM groups WHERE id = ?", (group_id,)).fetchone()
        if not row:
            return None
        return {"id": str(row[0]), "name": str(row[1])}
    finally:
        conn.close()


def insert_group(name: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO groups (name) VALUES (?)", (name,))
        conn.commit()
    finally:
        conn.close()


def update_group(group_id: int, name: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE groups SET name = ? WHERE id = ?", (name, group_id))
        conn.commit()
    finally:
        conn.close()


def delete_group(group_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
    finally:
        conn.close()


def fetch_students_for_table() -> list[tuple[int, str, str, str, str, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
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
        result: list[tuple[int, str, str, str, str, str]] = []
        for id, fio, group_name, san_date, med_date, flu_date in rows:
            result.append((int(id), str(fio), str(group_name), str(san_date), str(med_date), str(flu_date)))
        return result
    finally:
        conn.close()


def fetch_student_by_id(student_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if not row:
            return None

        keys = [
            "id",
            "group_id",
            "last_name",
            "first_name",
            "middle_name",
            "birth_date",
            "passport_series",
            "passport_number",
            "passport_issued_by",
            "passport_issue_date",
            "passport_department_code",
            "oms",
            "address",
            "sanminimum_date",
            "medical_exam_date",
            "fluorography_date",
        ]
        return {keys[i]: str(value) for i, value in enumerate(row)}
    finally:
        conn.close()


def update_student(student_id: int, data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            UPDATE students
            SET
                group_id = ?, last_name = ?, first_name = ?, middle_name = ?, birth_date = ?,
                passport_series = ?, passport_number = ?, passport_issued_by = ?, passport_issue_date = ?,
                passport_department_code = ?, oms = ?, address = ?,
                sanminimum_date = ?, medical_exam_date = ?, fluorography_date = ?
            WHERE id = ?
            """,
            (
                data["group_id"], data["last_name"], data["first_name"], data["middle_name"],
                data["birth_date"], data["passport_series"], data["passport_number"],
                data["passport_issued_by"], data["passport_issue_date"], data["passport_department_code"],
                data["oms"], data["address"], data["sanminimum_date"],
                data["medical_exam_date"], data["fluorography_date"],
                student_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_student(student_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
    finally:
        conn.close()


def insert_student(data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            INSERT INTO students (
                group_id, last_name, first_name, middle_name, birth_date,
                passport_series, passport_number, passport_issued_by, passport_issue_date,
                passport_department_code, oms, address,
                sanminimum_date, medical_exam_date, fluorography_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["group_id"], data["last_name"], data["first_name"], data["middle_name"],
                data["birth_date"], data["passport_series"], data["passport_number"],
                data["passport_issued_by"], data["passport_issue_date"], data["passport_department_code"],
                data["oms"], data["address"], data["sanminimum_date"],
                data["medical_exam_date"], data["fluorography_date"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_medicines_for_table() -> list[tuple[int, str, str, int, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, name, unit, quantity, expiration_date
            FROM medicines
            ORDER BY name
            """
        ).fetchall()
        return [(int(id), str(name), str(unit), int(quantity), str(exp_date)) for id, name, unit, quantity, exp_date in rows]
    finally:
        conn.close()


def fetch_medicine_by_id(medicine_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT id, name, unit, quantity, expiration_date FROM medicines WHERE id = ?", (medicine_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": str(row[0]),
            "name": str(row[1]),
            "unit": str(row[2]),
            "quantity": str(row[3]),
            "expiration_date": str(row[4]),
        }
    finally:
        conn.close()


def insert_medicine(data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO medicines (name, unit, quantity, expiration_date)
            VALUES (?, ?, ?, ?)
            """,
            (data["name"], data["unit"], int(data["quantity"]), data["expiration_date"]),
        )
        conn.commit()
    finally:
        conn.close()


def update_medicine(medicine_id: int, data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            UPDATE medicines
            SET name = ?, unit = ?, quantity = ?, expiration_date = ?
            WHERE id = ?
            """,
            (data["name"], data["unit"], int(data["quantity"]), data["expiration_date"], medicine_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_medicine(medicine_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
        conn.commit()
    finally:
        conn.close()


def fetch_all_person_names() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    try:
        emp = conn.execute("SELECT last_name, first_name, middle_name FROM employees").fetchall()
        stu = conn.execute("SELECT last_name, first_name, middle_name FROM students").fetchall()
        names = []
        for r in emp + stu:
            ln = r[0] or ""
            fn = r[1] or ""
            mn = r[2] or ""
            full = f"{ln} {fn} {mn}".strip()
            if full:
                full = " ".join(full.split())
                names.append(full)
        return sorted(list(set(names)))
    finally:
        conn.close()


def _format_initials(full_name: str) -> str:
    parts = full_name.split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    else:
        return f"{parts[0]} {parts[1][0]}. {parts[2][0]}."


def fetch_appeals_for_table() -> list[tuple[int, str, str, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, title, sender, created_at
            FROM appeals
            ORDER BY id DESC
            """
        ).fetchall()
        return [(int(id), str(title), _format_initials(str(sender)), str(created_at)) for id, title, sender, created_at in rows]
    finally:
        conn.close()


def fetch_appeal_by_id(appeal_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT id, title, text, sender, created_at FROM appeals WHERE id = ?", (appeal_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": str(row[0]),
            "title": str(row[1]),
            "text": str(row[2]),
            "sender": str(row[3]),
            "created_at": str(row[4]),
        }
    finally:
        conn.close()


def insert_appeal(data: dict[str, str]) -> None:
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    try:
        created_at = datetime.now().strftime("%d.%m.%Y")
        conn.execute(
            """
            INSERT INTO appeals (title, text, sender, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (data["title"], data["text"], data["sender"], created_at),
        )
        conn.commit()
    finally:
        conn.close()


def update_appeal(appeal_id: int, data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            UPDATE appeals
            SET title = ?, text = ?, sender = ?
            WHERE id = ?
            """,
            (data["title"], data["text"], data["sender"], appeal_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_appeal(appeal_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM appeals WHERE id = ?", (appeal_id,))
        conn.commit()
    finally:
        conn.close()

