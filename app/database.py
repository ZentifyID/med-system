import sqlite3
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Если запущен скомпилированный .exe, база будет лежать рядом с .exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Если запущен из исходников, база лежит в корне проекта
    BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "med_system.db"


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
        # Migration: Remove passport fields from students if they exist
        cursor = conn.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]
        if columns and "passport_series" in columns:
            conn.execute(
                """
                CREATE TABLE students_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    middle_name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
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
                INSERT INTO students_new (
                    id, group_id, last_name, first_name, middle_name, birth_date,
                    oms, address, sanminimum_date, medical_exam_date, fluorography_date
                )
                SELECT 
                    id, group_id, last_name, first_name, middle_name, birth_date,
                    oms, address, sanminimum_date, medical_exam_date, fluorography_date
                FROM students
                """
            )
            conn.execute("DROP TABLE students")
            conn.execute("ALTER TABLE students_new RENAME TO students")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                middle_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                oms TEXT NOT NULL,
                address TEXT NOT NULL,
                sanminimum_date TEXT NOT NULL,
                medical_exam_date TEXT NOT NULL,
                fluorography_date TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT
            )
            """
        )
        # Migration: Rename unit to dosage in medicines if exists
        cursor = conn.execute("PRAGMA table_info(medicines)")
        med_cols = [row[1] for row in cursor.fetchall()]
        if med_cols and "unit" in med_cols and "dosage" not in med_cols:
            conn.execute("ALTER TABLE medicines RENAME COLUMN unit TO dosage")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                expiration_date TEXT NOT NULL
            )
            """
        )
        # Migration: Check appeals schema
        cursor = conn.execute("PRAGMA table_info(appeals)")
        cols = [row[1] for row in cursor.fetchall()]
        if cols and "title" in cols:
            # Radical change requested - drop and recreate
            conn.execute("DROP TABLE appeals")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appeals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                sender TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                parent_phone TEXT NOT NULL,
                group_name TEXT NOT NULL,
                complaints TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                actions_recommendations TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_info (
                key TEXT PRIMARY KEY,
                value TEXT
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


def get_student_count_by_group(group_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        count = conn.execute("SELECT COUNT(*) FROM students WHERE group_id = ?", (group_id,)).fetchone()[0]
        return int(count)
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


def delete_group(group_id: int, cascade: bool = False) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        if cascade:
            conn.execute("DELETE FROM students WHERE group_id = ?", (group_id,))
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
                oms = ?, address = ?,
                sanminimum_date = ?, medical_exam_date = ?, fluorography_date = ?
            WHERE id = ?
            """,
            (
                data["group_id"], data["last_name"], data["first_name"], data["middle_name"],
                data["birth_date"], data["oms"], data["address"], data["sanminimum_date"],
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
                oms, address,
                sanminimum_date, medical_exam_date, fluorography_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["group_id"], data["last_name"], data["first_name"], data["middle_name"],
                data["birth_date"], data["oms"], data["address"], data["sanminimum_date"],
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
            SELECT id, name, dosage, quantity, expiration_date
            FROM medicines
            ORDER BY name
            """
        ).fetchall()
        return [(int(id), str(name), str(dosage), int(quantity), str(exp_date)) for id, name, dosage, quantity, exp_date in rows]
    finally:
        conn.close()


def fetch_medicine_by_id(medicine_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT id, name, dosage, quantity, expiration_date FROM medicines WHERE id = ?", (medicine_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": str(row[0]),
            "name": str(row[1]),
            "dosage": str(row[2]),
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
            INSERT INTO medicines (name, dosage, quantity, expiration_date)
            VALUES (?, ?, ?, ?)
            """,
            (data["name"], data["dosage"], int(data["quantity"]), data["expiration_date"]),
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
            SET name = ?, dosage = ?, quantity = ?, expiration_date = ?
            WHERE id = ?
            """,
            (data["name"], data["dosage"], int(data["quantity"]), data["expiration_date"], medicine_id),
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


def fetch_person_details_by_name(full_name: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        # Normalize name (remove extra spaces)
        full_name = " ".join(full_name.split())
        
        # Search in students
        row = conn.execute("""
            SELECT s.birth_date, g.name 
            FROM students s 
            JOIN groups g ON s.group_id = g.id
            WHERE (s.last_name || ' ' || s.first_name || ' ' || s.middle_name) = ?
        """, (full_name,)).fetchone()
        if row:
            return {"birth_date": row[0], "group_name": row[1]}
        
        # Search in employees
        row = conn.execute("""
            SELECT birth_date, affiliation
            FROM employees
            WHERE (last_name || ' ' || first_name || ' ' || middle_name) = ?
        """, (full_name,)).fetchone()
        if row:
            return {"birth_date": row[0], "group_name": row[1]}
            
        return None
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


def fetch_appeals_for_table() -> list[tuple[int, int, str, str, str]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, number, created_at, sender, complaints
            FROM appeals
            ORDER BY number DESC
            """
        ).fetchall()
        # id, number, date, sender, complaints
        return [(int(id), int(num), str(date), _format_initials(str(sender)), str(compl)) for id, num, date, sender, compl in rows]
    finally:
        conn.close()


def get_next_appeal_number() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT MAX(number) FROM appeals").fetchone()
        if row and row[0] is not None:
            return int(row[0]) + 1
        return 1
    finally:
        conn.close()


def fetch_appeal_by_id(appeal_id: int) -> dict[str, str] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT id, number, created_at, sender, birth_date, parent_phone, group_name, complaints, diagnosis, actions_recommendations 
            FROM appeals WHERE id = ?
            """, (appeal_id,)
        ).fetchone()
        if not row:
            return None
        keys = ["id", "number", "created_at", "sender", "birth_date", "parent_phone", "group_name", "complaints", "diagnosis", "actions_recommendations"]
        return {keys[i]: str(row[i]) for i in range(len(keys))}
    finally:
        conn.close()


def insert_appeal(data: dict[str, str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT INTO appeals (number, created_at, sender, birth_date, parent_phone, group_name, complaints, diagnosis, actions_recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(data["number"]), 
                data["created_at"], 
                data["sender"], 
                data["birth_date"], 
                data["parent_phone"], 
                data["group_name"], 
                data["complaints"], 
                data["diagnosis"], 
                data["actions_recommendations"]
            ),
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
            SET number = ?, created_at = ?, sender = ?, birth_date = ?, parent_phone = ?, group_name = ?, complaints = ?, diagnosis = ?, actions_recommendations = ?
            WHERE id = ?
            """,
            (
                int(data["number"]), 
                data["created_at"], 
                data["sender"], 
                data["birth_date"], 
                data["parent_phone"], 
                data["group_name"], 
                data["complaints"], 
                data["diagnosis"], 
                data["actions_recommendations"],
                appeal_id
            ),
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


def increment_first_digit_in_all_groups() -> int:
    import sqlite3
    import re
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT id, name FROM groups").fetchall()
        to_update = []
        for gid, name in rows:
            if name and name[0].isdigit():
                first_digit = int(name[0])
                new_name = str(first_digit + 1) + name[1:]
                if new_name != name:
                    to_update.append((gid, name, new_name, first_digit))
        
        # Sort by first digit descending to avoid UNIQUE constraint conflicts
        to_update.sort(key=lambda x: x[3], reverse=True)
        
        count = 0
        for gid, _, new_name, _ in to_update:
            try:
                conn.execute("UPDATE groups SET name = ? WHERE id = ?", (new_name, gid))
                count += 1
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        return count
    finally:
        conn.close()


def check_and_auto_increment_groups() -> int:
    from datetime import datetime
    now = datetime.now()
    # Threshold: August 15th
    if now.month < 8 or (now.month == 8 and now.day < 15):
        return 0
    
    current_year = str(now.year)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS system_info (key TEXT PRIMARY KEY, value TEXT)")
        row = conn.execute("SELECT value FROM system_info WHERE key = 'last_group_increment_year'").fetchone()
        last_year = row[0] if row else None
        
        if last_year == current_year:
            return 0
        
        count = increment_first_digit_in_all_groups()
        conn.execute("INSERT OR REPLACE INTO system_info (key, value) VALUES ('last_group_increment_year', ?)", (current_year,))
        conn.commit()
        return count
    finally:
        conn.close()

