"""Работа с сотрудниками."""
from app.db.connection import get_connection

# Единый список колонок — используется и в SELECT, и при сборке словаря,
# чтобы порядок никогда не разъехался.
EMPLOYEE_COLUMNS = [
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

_DATA_COLUMNS = EMPLOYEE_COLUMNS[1:]  # все, кроме id


def fetch_employees_for_table() -> list[tuple[int, str, str, str, str, str]]:
    with get_connection() as conn:
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


def fetch_employee_by_id(employee_id: int) -> dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {', '.join(EMPLOYEE_COLUMNS)} FROM employees WHERE id = ?",
            (employee_id,),
        ).fetchone()
    if not row:
        return None
    return {col: str(value) for col, value in zip(EMPLOYEE_COLUMNS, row)}


def insert_employee(data: dict[str, str]) -> None:
    placeholders = ", ".join("?" for _ in _DATA_COLUMNS)
    with get_connection() as conn:
        conn.execute(
            f"INSERT INTO employees ({', '.join(_DATA_COLUMNS)}) VALUES ({placeholders})",
            tuple(data[col] for col in _DATA_COLUMNS),
        )


def update_employee(employee_id: int, data: dict[str, str]) -> None:
    assignments = ", ".join(f"{col} = ?" for col in _DATA_COLUMNS)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE employees SET {assignments} WHERE id = ?",
            tuple(data[col] for col in _DATA_COLUMNS) + (employee_id,),
        )


def delete_employee(employee_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
