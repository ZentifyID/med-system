"""Схема базы данных: создание таблиц и миграции."""
import sqlite3

from app.db.connection import get_connection

DEFAULT_ICD_CODES = [
    ("J06.9", "ОРВИ (Острая респираторная вирусная инфекция)"),
    ("J00", "Острый назофарингит (насморк)"),
    ("J11", "Грипп, вирус не идентифицирован"),
    ("J10", "Грипп, вызванный идентифицированным вирусом гриппа"),
    ("J20.9", "Острый бронхит неуточненный"),
    ("J02.9", "Острый фарингит неуточненный"),
    ("J03.9", "Острый тонзиллит неуточненный (ангина)"),
    ("J35.0", "Хронический тонзиллит"),
    ("J30.4", "Аллергический ринит неуточненный"),
    ("S00.0", "Ушиб волосистой части головы"),
    ("S00.1", "Ушиб века и окологлазничной области"),
    ("S60.2", "Ушиб других частей запястья и кисти"),
    ("S90.3", "Ушиб других и неуточненных частей стопы"),
    ("T14.0", "Поверхностная травма неуточненной области (ссадина, царапина)"),
    ("T14.1", "Открытая рана неуточненной области тела"),
    ("S30.0", "Ушиб нижней части спины и таза"),
    ("S80.0", "Ушиб коленного сустава"),
    ("R51", "Головная боль"),
    ("R10.4", "Другие и неуточненные боли в области живота"),
    ("G90.8", "Вегетососудистая дистония (ВСД)"),
    ("K29.9", "Гастродуоденит неуточненный"),
    ("K29.7", "Гастрит неуточненный"),
    ("H52.1", "Миопия (близорукость)"),
    ("M41.9", "Сколиоз неуточненный"),
    ("M40.9", "Кифоз неуточненный"),
    ("L30.9", "Дерматит неуточненный"),
    ("H66.9", "Средний отит неуточненный"),
    ("J45.9", "Астма неуточненная"),
    ("E10.9", "Инсулинозависимый сахарный диабет (без осложнений)"),
    ("T78.4", "Аллергия неуточненная"),
    ("N30.9", "Цистит неуточненный"),
    ("K59.0", "Запор"),
    ("R11", "Тошнота и рвота"),
    ("R50.9", "Лихорадка неуточненная (повышенная температура)"),
]


def init_db() -> None:
    with get_connection() as conn:
        _create_tables(conn)
        _run_migrations(conn)
        _create_indexes(conn)
        _seed_icd_codes(conn)


def _create_tables(conn: sqlite3.Connection) -> None:
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
            dosage TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiration_date TEXT NOT NULL
        )
        """
    )
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS icd_codes (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )


def _run_migrations(conn: sqlite3.Connection) -> None:
    # Миграция: удаление паспортных полей у студентов (старые версии БД)
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

    # Миграция: переименование unit -> dosage в лекарствах
    cursor = conn.execute("PRAGMA table_info(medicines)")
    med_cols = [row[1] for row in cursor.fetchall()]
    if med_cols and "unit" in med_cols and "dosage" not in med_cols:
        conn.execute("ALTER TABLE medicines RENAME COLUMN unit TO dosage")

    # Миграция: старая схема обращений (с полем title) -> резервная копия
    cursor = conn.execute("PRAGMA table_info(appeals)")
    cols = [row[1] for row in cursor.fetchall()]
    if cols and "title" in cols:
        try:
            conn.execute("ALTER TABLE appeals RENAME TO appeals_backup_v1")
        except sqlite3.OperationalError:
            conn.execute("DROP TABLE appeals")
        # Пересоздаём таблицу по актуальной схеме
        _create_tables(conn)


def _create_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_group_id ON students(group_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_appeals_number ON appeals(number)")


def _seed_icd_codes(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM icd_codes").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO icd_codes (code, name) VALUES (?, ?)", DEFAULT_ICD_CODES
        )
