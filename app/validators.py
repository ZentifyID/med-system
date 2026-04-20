from datetime import datetime


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
