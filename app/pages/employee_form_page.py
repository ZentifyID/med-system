import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.validators import (
    AFFILIATION_UI_VALUES,
    DATE_FIELDS,
    FIELD_LABELS,
    allow_typed_value,
    normalize_affiliation,
    validate_employee_payload,
)

DATE_PLACEHOLDER = "__.__.____"


class EmployeeFormPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[dict[str, str]], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg="#f3f4f6")
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")
        self.form_vars: dict[str, tk.StringVar] = {}

        title = tk.Label(
            self,
            text="Добавление сотрудника",
            font=("Segoe UI", 18, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        title.pack(pady=(20, 12))

        fields: list[tuple[str, str]] = [
            ("last_name", FIELD_LABELS["last_name"]),
            ("first_name", FIELD_LABELS["first_name"]),
            ("middle_name", FIELD_LABELS["middle_name"]),
            ("birth_date", FIELD_LABELS["birth_date"]),
            ("affiliation", FIELD_LABELS["affiliation"]),
            ("passport_series", FIELD_LABELS["passport_series"]),
            ("passport_number", FIELD_LABELS["passport_number"]),
            ("passport_issued_by", FIELD_LABELS["passport_issued_by"]),
            ("passport_issue_date", FIELD_LABELS["passport_issue_date"]),
            ("passport_department_code", FIELD_LABELS["passport_department_code"]),
            ("oms", FIELD_LABELS["oms"]),
            ("address", FIELD_LABELS["address"]),
            ("sanminimum_date", FIELD_LABELS["sanminimum_date"]),
            ("medical_exam_date", FIELD_LABELS["medical_exam_date"]),
            ("fluorography_date", FIELD_LABELS["fluorography_date"]),
        ]

        form_container = tk.Frame(self, bg="#f3f4f6")
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        for i in range(2):
            form_container.grid_columnconfigure(i * 2, weight=0)
            form_container.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(fields) + 1) // 2
        for idx, (key, label) in enumerate(fields):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1

            tk.Label(
                form_container,
                text=label,
                font=("Segoe UI", 10),
                bg="#f3f4f6",
                fg="#111827",
                anchor="w",
            ).grid(row=row, column=label_col, sticky="w", padx=(0, 8), pady=6)

            var = tk.StringVar()
            self.form_vars[key] = var

            if key == "affiliation":
                field = ttk.Combobox(
                    form_container,
                    textvariable=var,
                    state="readonly",
                    values=AFFILIATION_UI_VALUES,
                )
                field.current(0)
            else:
                field = tk.Entry(
                    form_container,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    validate="key",
                    validatecommand=self._validate_cmd,
                    name=f"field_{key}",
                )
                if key in DATE_FIELDS:
                    field.bind("<FocusIn>", lambda _event, k=key: self._on_date_focus_in(k))
                    field.bind("<FocusOut>", lambda _event, k=key: self._on_date_focus_out(k))
                    field.bind("<KeyRelease>", lambda _event, k=key: self._format_date_input(k))

            field.grid(row=row, column=input_col, sticky="ew", padx=(0, 18), pady=6)

        hint = tk.Label(
            self,
            text="Формат дат: ДД.ММ.ГГГГ",
            font=("Segoe UI", 9, "italic"),
            bg="#f3f4f6",
            fg="#374151",
        )
        hint.pack(anchor="w", padx=22, pady=(0, 8))

        actions = tk.Frame(self, bg="#f3f4f6")
        actions.pack(fill=tk.X, padx=20, pady=(0, 18))

        save_button = tk.Button(
            actions,
            text="Сохранить",
            width=14,
            font=("Segoe UI", 10),
            command=self._submit,
        )
        save_button.pack(side=tk.LEFT)

        cancel_button = tk.Button(
            actions,
            text="Отмена",
            width=14,
            font=("Segoe UI", 10),
            command=self._on_cancel,
        )
        cancel_button.pack(side=tk.LEFT, padx=(10, 0))

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            if key == "affiliation":
                var.set(AFFILIATION_UI_VALUES[0])
            elif key in DATE_FIELDS:
                var.set(DATE_PLACEHOLDER)
            else:
                var.set("")

    def _validate_input(self, proposed_value: str, widget_path: str) -> bool:
        field_name = widget_path.split(".")[-1].replace("field_", "")
        if field_name not in self.form_vars:
            return True
        return allow_typed_value(field_name, proposed_value)

    def _submit(self) -> None:
        data = {key: var.get().strip() for key, var in self.form_vars.items()}
        for date_field in DATE_FIELDS:
            if data[date_field] == DATE_PLACEHOLDER:
                data[date_field] = ""
        data["affiliation"] = normalize_affiliation(data["affiliation"])

        errors = validate_employee_payload(data)
        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5]))
            return

        self._on_save(data)

    def _on_date_focus_in(self, field_name: str) -> None:
        if self.form_vars[field_name].get() == DATE_PLACEHOLDER:
            self.form_vars[field_name].set("")

    def _on_date_focus_out(self, field_name: str) -> None:
        if not self.form_vars[field_name].get().strip():
            self.form_vars[field_name].set(DATE_PLACEHOLDER)

    def _format_date_input(self, field_name: str) -> None:
        value = self.form_vars[field_name].get()
        if value == DATE_PLACEHOLDER:
            return

        digits = "".join(char for char in value if char.isdigit())[:8]
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}.{digits[2:]}"
        else:
            formatted = f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"
        self.form_vars[field_name].set(formatted)
