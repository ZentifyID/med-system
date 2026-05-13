from datetime import datetime, timedelta


AFFILIATION_UI_VALUES = ("основной", "внешний совместитель")

FIELD_LABELS = {
    "last_name": "Фамилия",
    "first_name": "Имя",
    "middle_name": "Отчество",
    "birth_date": "Дата рождения",
    "affiliation": "Принадлежность",
    "passport_series": "Паспорт: серия",
    "passport_number": "Паспорт: номер",
    "passport_issued_by": "Паспорт: кем выдан",
    "passport_issue_date": "Паспорт: дата выдачи",
    "passport_department_code": "Паспорт: код подразделения",
    "oms": "ОМС",
    "address": "Адрес проживания",
    "sanminimum_date": "Дата санминимума",
    "medical_exam_date": "Дата медосмотра",
    "fluorography_date": "Дата флюорографии",
}

FIELD_MAX_LENGTHS = {
    "last_name": 50,
    "first_name": 50,
    "middle_name": 50,
    "birth_date": 10,
    "affiliation": 32,
    "passport_series": 4,
    "passport_number": 6,
    "passport_issued_by": 255,
    "passport_issue_date": 10,
    "passport_department_code": 6,
    "oms": 16,
    "address": 255,
    "sanminimum_date": 10,
    "medical_exam_date": 10,
    "fluorography_date": 10,
    "group_id": 10,
}

LETTER_FIELDS = {"last_name", "first_name", "middle_name"}
DATE_FIELDS = {
    "birth_date",
    "passport_issue_date",
    "sanminimum_date",
    "medical_exam_date",
    "fluorography_date",
}
DIGITS_EXACT_LENGTH = {
    "passport_series": 4,
    "passport_number": 6,
    "passport_department_code": 6,
    "oms": 16,
}


def normalize_affiliation(affiliation_ui_value: str) -> str:
    if affiliation_ui_value == "внешний совместитель":
        return "внешний"
    return "основной"


def allow_typed_value(field: str, value: str) -> bool:
    max_len = FIELD_MAX_LENGTHS[field]
    if len(value) > max_len:
        return False

    if not value:
        return True

    if field in LETTER_FIELDS:
        return value.isalpha()

    if field in DIGITS_EXACT_LENGTH:
        return value.isdigit()

    if field in DATE_FIELDS:
        if not all(char.isdigit() or char == "." for char in value):
            return False
        if sum(char.isdigit() for char in value) > 8:
            return False
        return value.count(".") <= 2

    return True


def validate_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_employee_payload(payload: dict[str, str]) -> list[str]:
    errors: list[str] = []

    for field, label in FIELD_LABELS.items():
        if not payload.get(field, "").strip():
            errors.append(f"Поле '{label}' обязательно.")

    for field in LETTER_FIELDS:
        value = payload.get(field, "")
        if value and not value.isalpha():
            errors.append(f"Поле '{FIELD_LABELS[field]}' должно содержать только буквы.")

    for field in DATE_FIELDS:
        value = payload.get(field, "")
        if value and not validate_date(value):
            errors.append(
                f"Поле '{FIELD_LABELS[field]}' должно быть в формате ДД.ММ.ГГГГ и корректной датой."
            )

    for field, exact_len in DIGITS_EXACT_LENGTH.items():
        value = payload.get(field, "")
        if value and (not value.isdigit() or len(value) != exact_len):
            errors.append(
                f"Поле '{FIELD_LABELS[field]}' должно содержать ровно {exact_len} цифр."
            )

    for field, max_len in FIELD_MAX_LENGTHS.items():
        value = payload.get(field, "")
        if len(value) > max_len:
            errors.append(f"Поле '{FIELD_LABELS[field]}' не должно превышать {max_len} символов.")

    return errors


STUDENT_FIELD_LABELS = FIELD_LABELS.copy()
del STUDENT_FIELD_LABELS["affiliation"]
del STUDENT_FIELD_LABELS["passport_series"]
del STUDENT_FIELD_LABELS["passport_number"]
del STUDENT_FIELD_LABELS["passport_issued_by"]
del STUDENT_FIELD_LABELS["passport_issue_date"]
del STUDENT_FIELD_LABELS["passport_department_code"]
STUDENT_FIELD_LABELS["group_id"] = "Группа"

def validate_student_payload(payload: dict[str, str]) -> list[str]:
    errors: list[str] = []

    for field, label in STUDENT_FIELD_LABELS.items():
        if not payload.get(field, "").strip():
            errors.append(f"Поле '{label}' обязательно.")

    for field in LETTER_FIELDS:
        value = payload.get(field, "")
        if value and not value.isalpha():
            errors.append(f"Поле '{STUDENT_FIELD_LABELS[field]}' должно содержать только буквы.")

    for field in DATE_FIELDS:
        value = payload.get(field, "")
        if value and not validate_date(value):
            errors.append(
                f"Поле '{STUDENT_FIELD_LABELS[field]}' должно быть в формате ДД.ММ.ГГГГ и корректной датой."
            )

    for field, exact_len in DIGITS_EXACT_LENGTH.items():
        value = payload.get(field, "")
        if value and (not value.isdigit() or len(value) != exact_len):
            errors.append(
                f"Поле '{STUDENT_FIELD_LABELS[field]}' должно содержать ровно {exact_len} цифр."
            )

    for field, max_len in FIELD_MAX_LENGTHS.items():
        if field == "affiliation": continue
        value = payload.get(field, "")
        if len(value) > max_len:
            errors.append(f"Поле '{STUDENT_FIELD_LABELS[field]}' не должно превышать {max_len} символов.")

    # Validate group_id is a valid integer
    group_id = payload.get("group_id", "")
    if group_id and not group_id.isdigit():
         errors.append("Некорректный ID группы.")

    return errors


def get_person_expiration_status(dates: list[str]) -> tuple[bool, bool]:
    """Returns (is_expired, is_expiring) for a list of person dates (med, san, flu)."""
    now = datetime.now()
    fourteen_days = now + timedelta(days=14)
    exp_dates = []
    for d_str in dates:
        try:
            d = datetime.strptime(d_str, "%d.%m.%Y")
            try:
                exp = d.replace(year=d.year + 1)
            except ValueError:
                exp = d.replace(year=d.year + 1, month=2, day=28)
            exp_dates.append(exp)
        except ValueError:
            pass
    is_expired = any(e < now for e in exp_dates)
    is_expiring = any(now <= e <= fourteen_days for e in exp_dates)
    return is_expired, is_expiring

def get_medicine_expiration_status(exp_date_str: str) -> tuple[bool, bool]:
    """Returns (is_expired, is_expiring) for a medicine expiration date."""
    now = datetime.now()
    fourteen_days = now + timedelta(days=14)
    is_expired = is_expiring = False
    if exp_date_str:
        try:
            d = datetime.strptime(exp_date_str, "%d.%m.%Y")
            is_expired = d < now
            is_expiring = d <= fourteen_days
        except ValueError:
            pass
    return is_expired, is_expiring
