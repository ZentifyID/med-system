"""Работа с лекарствами."""
from app.db.connection import get_connection


def fetch_medicines_for_table() -> list[tuple[int, str, str, int, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, dosage, quantity, expiration_date
            FROM medicines
            ORDER BY name
            """
        ).fetchall()
    return [
        (int(id), str(name), str(dosage), int(quantity), str(exp_date))
        for id, name, dosage, quantity, exp_date in rows
    ]


def fetch_medicine_by_id(medicine_id: int) -> dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, dosage, quantity, expiration_date FROM medicines WHERE id = ?",
            (medicine_id,),
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


def insert_medicine(data: dict[str, str]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO medicines (name, dosage, quantity, expiration_date)
            VALUES (?, ?, ?, ?)
            """,
            (data["name"], data["dosage"], int(data["quantity"]), data["expiration_date"]),
        )


def update_medicine(medicine_id: int, data: dict[str, str]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE medicines
            SET name = ?, dosage = ?, quantity = ?, expiration_date = ?
            WHERE id = ?
            """,
            (data["name"], data["dosage"], int(data["quantity"]), data["expiration_date"], medicine_id),
        )


def delete_medicine(medicine_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))


def reorder_medicines(items: list[dict]) -> None:
    """Списывает старые партии и добавляет новые ОДНОЙ транзакцией:
    если что-то пойдёт не так, база останется в исходном состоянии."""
    with get_connection() as conn:
        for item in items:
            conn.execute("DELETE FROM medicines WHERE id = ?", (int(item["old_id"]),))
            conn.execute(
                """
                INSERT INTO medicines (name, dosage, quantity, expiration_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    item["name"],
                    item["dosage"],
                    int(item["new_quantity"]),
                    item["new_expiration_date"],
                ),
            )
