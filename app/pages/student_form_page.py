import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, DateMaskHandler
)
from app.validators import DATE_FIELDS, STUDENT_FIELD_LABELS as FIELD_LABELS, validate_student_payload, allow_typed_value

DATE_PLACEHOLDER = "__.__.____"

FIELDS: list[tuple[str, str]] = [
    ("last_name", FIELD_LABELS["last_name"]),
    ("first_name", FIELD_LABELS["first_name"]),
    ("middle_name", FIELD_LABELS["middle_name"]),
    ("birth_date", FIELD_LABELS["birth_date"]),
    ("group_id", FIELD_LABELS["group_id"]),
    ("oms", FIELD_LABELS["oms"]),
    ("address", FIELD_LABELS["address"]),
    ("sanminimum_date", FIELD_LABELS["sanminimum_date"]),
    ("medical_exam_date", FIELD_LABELS["medical_exam_date"]),
    ("fluorography_date", FIELD_LABELS["fluorography_date"]),
]


class StudentFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Entry | ctk.CTkEntry] = {}
        self.group_mapping: dict[str, str] = {}
        self.group_combobox: ctk.CTkComboBox | None = None

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        tk.Label(hdr, text="Добавление студента", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        
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

            if key == "group_id":
                cb = ctk.CTkComboBox(
                    inner, variable=var, state="readonly", font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
                    fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
                    button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=40
                )
                cb.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
                self.group_combobox = cb
            else:
                vcmd = (self.register(lambda p, k=key: allow_typed_value(k, p)), "%P")
                entry = ctk.CTkEntry(
                    inner,
                    textvariable=var,
                    font=(FONT_FAMILY, 14),
                    fg_color=ENTRY_BG,
                    text_color=ENTRY_FG,
                    border_color=ENTRY_BORDER,
                    corner_radius=CORNER_RADIUS,
                    height=40,
                    validate="key",
                    validatecommand=vcmd,
                )
                entry.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
                self.form_entries[key] = entry
                if key in DATE_FIELDS:
                    DateMaskHandler.bind_to_entry(entry, var)

        tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=(FONT_FAMILY, 9, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=36, pady=(0, 8))
        
        # Actions
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=36, pady=(0, 32))
        
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, height=44, width=160).pack(side=tk.RIGHT)
        FlatButton(actions, primary=False, text="Отмена", command=self._on_cancel, height=44, width=120).pack(side=tk.RIGHT, padx=(0, 12))

    def set_groups(self, groups: list[tuple[int, str]]) -> None:
        self.group_mapping = {name: str(id) for id, name in groups}
        if self.group_combobox:
            vals = list(self.group_mapping.keys())
            self.group_combobox.configure(values=vals)
            if vals:
                self.form_vars["group_id"].set(vals[0])

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            if key in DATE_FIELDS:
                var.set(DATE_PLACEHOLDER)
            elif key != "group_id":
                var.set("")

    def _submit(self) -> None:
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data.get(f) == DATE_PLACEHOLDER: data[f] = ""
        group_name = data["group_id"]
        data["group_id"] = self.group_mapping.get(group_name, "")
        errors = validate_student_payload(data)
        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5]))
            return
        self._on_save(data)


