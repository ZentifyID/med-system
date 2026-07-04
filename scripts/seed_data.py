"""Наполнение базы тестовыми данными для проверки программы.

Запуск из корня проекта:
    python -m scripts.seed_data              # добавить данные
    python -m scripts.seed_data --reset      # очистить базу и наполнить заново

Создаёт: группы, студентов, сотрудников, лекарства, обращения.
Специально добавляет «проблемные» записи для проверки фильтров:
просроченные медосмотры, истекающие сроки, лекарства с малым остатком.
"""
import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Чтобы скрипт работал при запуске и как модуль, и напрямую
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import (
    init_db, insert_group, fetch_groups, insert_student, insert_employee,
    insert_medicine, insert_appeal, get_next_appeal_number,
    fetch_students_for_table, fetch_employees_for_table,
    fetch_medicines_for_table, fetch_appeals_for_table, search_icd_codes,
)
from app.db.connection import get_connection

random.seed()  # каждый запуск — разные данные

# ── Справочники имён ─────────────────────────────────────────────────
MALE = {
    "last": ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов",
             "Волков", "Соколов", "Морозов", "Новиков", "Фёдоров", "Козлов",
             "Лебедев", "Егоров", "Павлов", "Степанов", "Николаев", "Орлов"],
    "first": ["Александр", "Дмитрий", "Максим", "Иван", "Артём", "Никита",
              "Михаил", "Даниил", "Егор", "Андрей", "Кирилл", "Алексей",
              "Илья", "Сергей", "Владислав", "Тимур", "Арсен", "Роман"],
    "middle": ["Александрович", "Дмитриевич", "Сергеевич", "Иванович",
               "Андреевич", "Михайлович", "Алексеевич", "Владимирович",
               "Николаевич", "Петрович", "Русланович", "Олегович"],
}
FEMALE = {
    "last": ["Иванова", "Петрова", "Сидорова", "Кузнецова", "Смирнова",
             "Попова", "Волкова", "Соколова", "Морозова", "Новикова",
             "Фёдорова", "Козлова", "Лебедева", "Егорова", "Павлова",
             "Степанова", "Николаева", "Орлова"],
    "first": ["Анастасия", "Мария", "Дарья", "Анна", "Елизавета", "Полина",
              "Виктория", "Екатерина", "Софья", "Алиса", "Ксения", "Алина",
              "Валерия", "Вероника", "Арина", "Диана", "Милана", "Кира"],
    "middle": ["Александровна", "Дмитриевна", "Сергеевна", "Ивановна",
               "Андреевна", "Михайловна", "Алексеевна", "Владимировна",
               "Николаевна", "Петровна", "Руслановна", "Олеговна"],
}

STREETS = ["Ленина", "Мира", "Гагарина", "Советская", "Центральная",
           "Молодёжная", "Школьная", "Садовая", "Октябрьская", "Пушкина"]

MEDICINES = [
    ("Парацетамол", "500 мг"), ("Ибупрофен", "400 мг"), ("Анальгин", "500 мг"),
    ("Аспирин", "500 мг"), ("Но-шпа", "40 мг"), ("Супрастин", "25 мг"),
    ("Лоратадин", "10 мг"), ("Активированный уголь", "250 мг"),
    ("Валидол", "60 мг"), ("Корвалол", "25 мл"), ("Йод", "5% 10 мл"),
    ("Перекись водорода", "3% 100 мл"), ("Бинт стерильный", "5м x 10см"),
    ("Пластырь бактерицидный", "19x72 мм"), ("Хлоргексидин", "0.05% 100 мл"),
    ("Нурофен", "200 мг"), ("Смекта", "3 г"), ("Регидрон", "18.9 г"),
    ("Амброксол", "30 мг"), ("Каметон", "45 г"),
]

COMPLAINTS = [
    "Головная боль, слабость", "Боль в горле, температура 37.5",
    "Ушиб колена на физкультуре", "Тошнота, боль в животе",
    "Насморк, чихание", "Порез пальца", "Головокружение",
    "Боль в спине", "Аллергическая сыпь на руках", "Кашель, першение в горле",
    "Повышенная температура 38.1", "Ссадина на локте",
    "Боль в ухе", "Носовое кровотечение", "Обморок на перемене",
]

ACTIONS = [
    "Осмотр, измерение температуры. Отправлен(а) домой, рекомендовано обратиться к участковому врачу.",
    "Обработка раны антисептиком, наложена повязка. Наблюдение.",
    "Дан парацетамол 500 мг. Отдых в медпункте 30 минут, состояние улучшилось.",
    "Измерено давление, дан валидол. Рекомендован покой.",
    "Холодный компресс на место ушиба. Рекомендован рентген при усилении боли.",
    "Дан супрастин 25 мг. Рекомендована консультация аллерголога.",
    "Промывание, обработка йодом. Наложен пластырь.",
]


def _fmt(d: datetime) -> str:
    return d.strftime("%d.%m.%Y")


def rand_person(gender: dict) -> tuple[str, str, str]:
    return (random.choice(gender["last"]), random.choice(gender["first"]),
            random.choice(gender["middle"]))


def rand_checkup_dates() -> dict[str, str]:
    """Даты санминимума/медосмотра/флюорографии.
    Документ действует год, поэтому:
      ~15% — просроченные (пройдены больше года назад),
      ~15% — истекают в ближайшие 2 недели,
      остальные — в норме."""
    today = datetime.now()
    result = {}
    for key in ("sanminimum_date", "medical_exam_date", "fluorography_date"):
        roll = random.random()
        if roll < 0.15:      # просрочен: пройден 13-18 месяцев назад
            d = today - timedelta(days=random.randint(395, 550))
        elif roll < 0.30:    # истекает: пройден ~год назад минус 0-14 дней
            d = today - timedelta(days=365 - random.randint(0, 14))
        else:                # в норме: пройден 1-10 месяцев назад
            d = today - timedelta(days=random.randint(30, 300))
        result[key] = _fmt(d)
    return result


def rand_birth_date(age_from: int, age_to: int) -> str:
    days = random.randint(age_from * 365, age_to * 365)
    return _fmt(datetime.now() - timedelta(days=days))


def rand_oms() -> str:
    return "".join(random.choices("0123456789", k=16))


def rand_address() -> str:
    return (f"г. Каспийск, ул. {random.choice(STREETS)}, "
            f"д. {random.randint(1, 120)}, кв. {random.randint(1, 90)}")


def rand_phone() -> str:
    return f"+79{random.randint(100000000, 999999999)}"


def seed_groups() -> list[tuple[int, str]]:
    letters = ["А", "Б", "В"]
    specialties = ["ИС", "СА", "БУ", "ПР"]
    for course in (1, 2, 3, 4):
        for spec in random.sample(specialties, k=2):
            name = f"{course}{random.randint(1, 2)}-{spec}-{random.choice(letters)}"
            try:
                insert_group(name)
            except Exception:
                pass  # такое имя уже есть
    groups = fetch_groups()
    print(f"  Группы: {len(groups)}")
    return groups


def seed_students(groups: list, count: int) -> None:
    for _ in range(count):
        gender = random.choice((MALE, FEMALE))
        last, first, middle = rand_person(gender)
        insert_student({
            "group_id": str(random.choice(groups)[0]),
            "last_name": last, "first_name": first, "middle_name": middle,
            "birth_date": rand_birth_date(15, 19),
            "oms": rand_oms(),
            "address": rand_address(),
            **rand_checkup_dates(),
        })
    print(f"  Студенты: +{count}")


def seed_employees(count: int) -> None:
    for _ in range(count):
        gender = random.choice((MALE, FEMALE))
        last, first, middle = rand_person(gender)
        issue = datetime.now() - timedelta(days=random.randint(365, 365 * 15))
        insert_employee({
            "last_name": last, "first_name": first, "middle_name": middle,
            "birth_date": rand_birth_date(25, 60),
            "affiliation": random.choice(("основной", "основной", "основной", "внешний")),
            "passport_series": "".join(random.choices("0123456789", k=4)),
            "passport_number": "".join(random.choices("0123456789", k=6)),
            "passport_issued_by": "МВД по Республике Дагестан",
            "passport_issue_date": _fmt(issue),
            "passport_department_code": "".join(random.choices("0123456789", k=6)),
            "oms": rand_oms(),
            "address": rand_address(),
            **rand_checkup_dates(),
        })
    print(f"  Сотрудники: +{count}")


def seed_medicines() -> None:
    today = datetime.now()
    for name, dosage in MEDICINES:
        roll = random.random()
        if roll < 0.15:      # просрочено
            exp = today - timedelta(days=random.randint(5, 200))
        elif roll < 0.30:    # истекает в ближайшие 2 недели
            exp = today + timedelta(days=random.randint(0, 14))
        else:                # в норме
            exp = today + timedelta(days=random.randint(60, 720))
        qty = random.choice((2, 3, 5)) if random.random() < 0.25 else random.randint(8, 60)
        insert_medicine({
            "name": name, "dosage": dosage,
            "quantity": str(qty), "expiration_date": _fmt(exp),
        })
    print(f"  Лекарства: +{len(MEDICINES)}")


def seed_appeals(count: int) -> None:
    students = fetch_students_for_table()
    icd = search_icd_codes("")  # первые 30 кодов
    if not students:
        print("  Обращения: пропущено (нет студентов)")
        return
    for _ in range(count):
        s = random.choice(students)
        diag = random.choice(icd) if icd else {"code": "J06.9", "name": "ОРВИ"}
        created = datetime.now() - timedelta(days=random.randint(0, 180))
        insert_appeal({
            "number": str(get_next_appeal_number()),
            "created_at": _fmt(created),
            "sender": s[1],                # ФИО
            "birth_date": rand_birth_date(15, 19),
            "parent_phone": rand_phone(),
            "group_name": s[2],
            "complaints": random.choice(COMPLAINTS),
            "diagnosis": f"{diag['code']} - {diag['name']}",
            "actions_recommendations": random.choice(ACTIONS),
        })
    print(f"  Обращения: +{count}")


def reset_db() -> None:
    with get_connection() as conn:
        for table in ("appeals", "students", "employees", "medicines", "groups"):
            conn.execute(f"DELETE FROM {table}")
    print("  База очищена (справочник МКБ сохранён)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Наполнение базы тестовыми данными")
    parser.add_argument("--reset", action="store_true", help="очистить базу перед наполнением")
    parser.add_argument("--students", type=int, default=120, help="сколько студентов (по умолч. 120)")
    parser.add_argument("--employees", type=int, default=25, help="сколько сотрудников (по умолч. 25)")
    parser.add_argument("--appeals", type=int, default=60, help="сколько обращений (по умолч. 60)")
    args = parser.parse_args()

    init_db()
    if args.reset:
        reset_db()

    print("Наполнение базы:")
    groups = seed_groups()
    seed_students(groups, args.students)
    seed_employees(args.employees)
    seed_medicines()
    seed_appeals(args.appeals)

    print("\nИтого в базе:")
    print(f"  Студентов:   {len(fetch_students_for_table())}")
    print(f"  Сотрудников: {len(fetch_employees_for_table())}")
    print(f"  Лекарств:    {len(fetch_medicines_for_table())}")
    print(f"  Обращений:   {len(fetch_appeals_for_table())}")


if __name__ == "__main__":
    main()
