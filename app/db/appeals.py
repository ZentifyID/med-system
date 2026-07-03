"""Работа с обращениями."""
from app.db.connection import get_connection

APPEAL_COLUMNS = [
    "id",
    "number",
    "created_at",
    "sender",
    "birth_date",
    "parent_phone",
    "group_name",
    "complaints",
    "diagnosis",
    "actions_recommendations",
]

_DATA_COLUMNS = APPEAL_COLUMNS[1:]  # все, кроме id


def _format_initials(full_name: str) -> str:
    parts = full_name.split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    return f"{parts[0]} {parts[1][0]}. {parts[2][0]}."


def fetch_appeals_for_table() -> list[tuple[int, int, str, str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, number, created_at, sender, complaints
            FROM appeals
            ORDER BY number DESC
            """
        ).fetchall()
    return [
        (int(id), int(num), str(date), _format_initials(str(sender)), str(compl))
        for id, num, date, sender, compl in rows
    ]


def get_next_appeal_number() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT MAX(number) FROM appeals").fetchone()
    if row and row[0] is not None:
        return int(row[0]) + 1
    return 1


def fetch_appeal_by_id(appeal_id: int) -> dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            f"SELECT {', '.join(APPEAL_COLUMNS)} FROM appeals WHERE id = ?",
            (appeal_id,),
        ).fetchone()
    if not row:
        return None
    return {col: str(value) for col, value in zip(APPEAL_COLUMNS, row)}


def insert_appeal(data: dict[str, str]) -> None:
    placeholders = ", ".join("?" for _ in _DATA_COLUMNS)
    values = [int(data["number"])] + [data[col] for col in _DATA_COLUMNS[1:]]
    with get_connection() as conn:
        conn.execute(
            f"INSERT INTO appeals ({', '.join(_DATA_COLUMNS)}) VALUES ({placeholders})",
            tuple(values),
        )


def update_appeal(appeal_id: int, data: dict[str, str]) -> None:
    assignments = ", ".join(f"{col} = ?" for col in _DATA_COLUMNS)
    values = [int(data["number"])] + [data[col] for col in _DATA_COLUMNS[1:]] + [appeal_id]
    with get_connection() as conn:
        conn.execute(
            f"UPDATE appeals SET {assignments} WHERE id = ?",
            tuple(values),
        )


def delete_appeal(appeal_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM appeals WHERE id = ?", (appeal_id,))


def fetch_persons_for_combobox() -> list[dict]:
    """Сотрудники и студенты одним списком — для выпадающего списка
    отправителя в форме обращения."""
    with get_connection() as conn:
        emp = conn.execute(
            "SELECT id, last_name, first_name, middle_name, birth_date, affiliation FROM employees"
        ).fetchall()
        stu = conn.execute(
            """
            SELECT s.id, s.last_name, s.first_name, s.middle_name, s.birth_date, g.name
            FROM students s JOIN groups g ON s.group_id = g.id
            """
        ).fetchall()

    persons = []
    for r in emp:
        fio = " ".join(f"{r[1] or ''} {r[2] or ''} {r[3] or ''}".split())
        persons.append({
            "display": f"{fio} (Сотрудник, {r[5]})",
            "birth_date": str(r[4]),
            "group_name": str(r[5]),
        })
    for r in stu:
        fio = " ".join(f"{r[1] or ''} {r[2] or ''} {r[3] or ''}".split())
        persons.append({
            "display": f"{fio} (Группа {r[5]})",
            "birth_date": str(r[4]),
            "group_name": str(r[5]),
        })
    return sorted(persons, key=lambda x: x["display"])
