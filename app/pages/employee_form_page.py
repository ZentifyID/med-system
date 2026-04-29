import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, DateMaskHandler
)
from app.validators import (
    AFFILIATION_UI_VALUES, DATE_FIELDS, FIELD_LABELS,
    normalize_affiliation, validate_employee_payload,
)

DATE_PLACEHOLDER = "__.__.____"

FIELDS: list[tuple[str, str]] = [
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


def _styled_entry(parent, var, key, validate_cmd):
    """Return a styled Entry or Combobox for a form field."""
    if key == "affiliation":
        w = ttk.Combobox(parent, textvariable=var, state="readonly", values=AFFILIATION_UI_VALUES, font=(FONT_FAMILY, 10))
        w.current(0)
        return w
    entry = ctk.CTkEntry(
        parent,
        textvariable=var,
        font=(FONT_FAMILY, 14),
        fg_color=ENTRY_BG,
        text_color=ENTRY_FG,
        border_color=ENTRY_BORDER,
        corner_radius=CORNER_RADIUS,
        height=40,
    )
    return entry


class EmployeeFormPage(tk.Frame):
    def __init__(self, master: tk.Misc, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Entry | ctk.CTkEntry] = {}

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        tk.Label(hdr, text="Добавление сотрудника", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        
        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 24))

        # Card Container
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 24))
        
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        for i in range(4):
            inner.grid_columnconfigure(i * 2 + (1 if i % 2 else 1), weight=1)
        for i in range(2):
            inner.grid_columnconfigure(i * 2, weight=0)
            inner.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(FIELDS) + 1) // 2
        for idx, (key, label) in enumerate(FIELDS):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1

            tk.Label(inner, text=label, font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=label_col, sticky="w", padx=(0 if block == 0 else 32, 8), pady=(8, 2))

            var = tk.StringVar()
            self.form_vars[key] = var
            widget = _styled_entry(inner, var, key, None)
            widget.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)

            # Get actual entry for date bindings
            if isinstance(widget, ctk.CTkEntry):
                self.form_entries[key] = widget
                if key in DATE_FIELDS:
                    DateMaskHandler.bind_to_entry(widget, var)

        tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=(FONT_FAMILY, 9, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=36, pady=(0, 8))

        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=36, pady=(0, 32))
        
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, height=44, width=160).pack(side=tk.RIGHT)
        FlatButton(actions, primary=False, text="Отмена", command=self._on_cancel, height=44, width=120).pack(side=tk.RIGHT, padx=(0, 12))

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            if key == "affiliation":
                var.set(AFFILIATION_UI_VALUES[0])
            elif key in DATE_FIELDS:
                var.set(DATE_PLACEHOLDER)
            else:
                var.set("")

    def _submit(self) -> None:
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data[f] == DATE_PLACEHOLDER:
                data[f] = ""
        data["affiliation"] = normalize_affiliation(data["affiliation"])
        errors = validate_employee_payload(data)
        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5]))
            return
        self._on_save(data)


