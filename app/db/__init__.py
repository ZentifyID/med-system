"""Слой данных: единая точка доступа ко всем операциям с БД.

Использование: from app.db import fetch_employees_for_table, ...

При переходе на PostgreSQL меняется только внутренность этого пакета,
интерфейс для остального приложения остаётся прежним.
"""
from app.db.schema import init_db
from app.db.employees import (
    fetch_employees_for_table,
    fetch_employee_by_id,
    insert_employee,
    update_employee,
    delete_employee,
)
from app.db.students import (
    fetch_students_for_table,
    fetch_student_by_id,
    insert_student,
    update_student,
    delete_student,
)
from app.db.groups import (
    fetch_groups,
    fetch_group_by_id,
    get_student_count_by_group,
    insert_group,
    update_group,
    delete_group,
    increment_first_digit_in_all_groups,
    check_and_auto_increment_groups,
)
from app.db.medicines import (
    fetch_medicines_for_table,
    fetch_medicine_by_id,
    insert_medicine,
    update_medicine,
    delete_medicine,
    reorder_medicines,
)
from app.db.appeals import (
    fetch_appeals_for_table,
    fetch_appeal_by_id,
    insert_appeal,
    update_appeal,
    delete_appeal,
    get_next_appeal_number,
    fetch_persons_for_combobox,
)
from app.db.icd import (
    search_icd_codes,
    fetch_all_icd_codes,
    insert_icd_code,
    update_icd_code,
    delete_icd_code,
)

__all__ = [
    "init_db",
    # employees
    "fetch_employees_for_table", "fetch_employee_by_id",
    "insert_employee", "update_employee", "delete_employee",
    # students
    "fetch_students_for_table", "fetch_student_by_id",
    "insert_student", "update_student", "delete_student",
    # groups
    "fetch_groups", "fetch_group_by_id", "get_student_count_by_group",
    "insert_group", "update_group", "delete_group",
    "increment_first_digit_in_all_groups", "check_and_auto_increment_groups",
    # medicines
    "fetch_medicines_for_table", "fetch_medicine_by_id",
    "insert_medicine", "update_medicine", "delete_medicine", "reorder_medicines",
    # appeals
    "fetch_appeals_for_table", "fetch_appeal_by_id",
    "insert_appeal", "update_appeal", "delete_appeal",
    "get_next_appeal_number", "fetch_persons_for_combobox",
    # icd
    "search_icd_codes", "fetch_all_icd_codes",
    "insert_icd_code", "update_icd_code", "delete_icd_code",
]
