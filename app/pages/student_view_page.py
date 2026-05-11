import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, cast

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, DateMaskHandler
)
from app.validators import DATE_FIELDS, STUDENT_FIELD_LABELS as FIELD_LABELS, validate_student_payload

DATE_PLACEHOLDER = "__.__.____"

FIELDS: list[tuple[str, str]] = [
    ("last_name", FIELD_LABELS["last_name"]),
    ("first_name", FIELD_LABELS["first_name"]),
    ("middle_name", FIELD_LABELS["middle_name"]),
    ("birth_date", FIELD_LABELS["birth_date"]),
    ("group_id", FIELD_LABELS["group_id"]),
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


class StudentViewPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[int, dict], None], on_delete: Callable[[int], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel

        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Widget] = {}
        self.form_labels: dict[str, tk.Label] = {}
        self.original_data: dict | None = None
        self.student_id: int | None = None
        self.is_edit_mode = False
        self.group_mapping: dict[str, str] = {}
        self.group_mapping_reverse: dict[str, str] = {}
        self.group_combobox: ctk.CTkComboBox | None = None

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        self.title_label = tk.Label(hdr, text="Студент", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side=tk.LEFT)
        
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
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 16))
        
        self.form_container = tk.Frame(card, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        for i in range(2):
            self.form_container.grid_columnconfigure(i * 2, weight=0)
            self.form_container.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(FIELDS) + 1) // 2
        for idx, (key, label) in enumerate(FIELDS):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1
            
            tk.Label(self.form_container, text=label, font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=label_col, sticky="w", padx=(0 if block == 0 else 32, 8), pady=8)

            var = tk.StringVar()
            self.form_vars[key] = var

            # View label
            val_label = tk.Label(self.form_container, textvariable=var, font=(FONT_FAMILY, 11), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
            val_label.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=8)
            self.form_labels[key] = val_label

            # Edit widget
            if key == "group_id":
                field = ctk.CTkComboBox(
                    self.form_container, variable=var, state="readonly", font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
                    fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
                    button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=40
                )
                self.group_combobox = field
            else:
                field = ctk.CTkEntry(
                    self.form_container,
                    textvariable=var,
                    font=(FONT_FAMILY, 14),
                    fg_color=ENTRY_BG,
                    text_color=ENTRY_FG,
                    border_color=ENTRY_BORDER,
                    corner_radius=CORNER_RADIUS,
                    height=40,
                )
                if key in DATE_FIELDS:
                    DateMaskHandler.bind_to_entry(field, var)
            self.form_entries[key] = field

        self.date_info = tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=(FONT_FAMILY, 9, "italic"), bg=BG_COLOR, fg=TEXT_MUTED)
        self.date_info.pack(anchor="w", padx=36, pady=(0, 8))
        self.date_info.pack_forget()

        # Actions
        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=36, pady=(0, 32))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, height=44, width=140)
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить", command=self._delete_student, height=44, width=120)
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, height=44, width=100)
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, height=44, width=160)
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, height=44, width=120)

        self._show_view_actions()

    def _show_view_actions(self):
        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(12, 0))
        self.back_button.pack(side=tk.RIGHT)

    def set_groups(self, groups: list[tuple[int, str]]) -> None:
        self.group_mapping = {name: str(id) for id, name in groups}
        self.group_mapping_reverse = {str(id): name for id, name in groups}
        if self.group_combobox:
            self.group_combobox.configure(values=list(self.group_mapping.keys()))
            if self.original_data:
                gid = self.original_data.get("group_id", "")
                self.form_vars["group_id"].set(self.group_mapping_reverse.get(gid, ""))

    def set_student_data(self, data: dict) -> None:
        try:
            self.student_id = int(data.get("id", 0))
        except (ValueError, TypeError):
            self.student_id = None
        self.original_data = data.copy()
        
        fio_parts = [data.get('last_name'), data.get('first_name'), data.get('middle_name')]
        fio = " ".join(part for part in fio_parts if part).strip()
        self.title_label.config(text=f"Студент: {fio}")
        
        self._update_form_vars(data)
        if self.is_edit_mode:
            self._toggle_edit_mode()

    def _update_form_vars(self, data: dict) -> None:
        for key, var in self.form_vars.items():
            value = data.get(key, "")
            if key == "group_id":
                var.set(self.group_mapping_reverse.get(value, ""))
            else:
                var.set(value)

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.pack_forget()
            self.delete_button.pack_forget()
            self.back_button.pack_forget()
            self.save_button.pack(side=tk.RIGHT)
            self.cancel_button.pack(side=tk.RIGHT, padx=(0, 12))
            self.date_info.pack(anchor="w", padx=36, pady=(0, 8))
            for key, lbl in self.form_labels.items():
                gi = lbl.grid_info()
                lbl.grid_remove()
                self.form_entries[key].grid(row=gi["row"], column=gi["column"], sticky="ew", padx=(0, 8 if gi["column"] == 1 else 0), pady=4)
        else:
            self.save_button.pack_forget()
            self.cancel_button.pack_forget()
            self.date_info.pack_forget()
            self._show_view_actions()
            for key, entry in self.form_entries.items():
                entry.grid_remove()
                self.form_labels[key].grid()

    def _cancel_edit(self) -> None:
        if self.original_data:
            self._update_form_vars(self.original_data)
        self._toggle_edit_mode()

    def _delete_student(self) -> None:
        if self.student_id and messagebox.askyesno("Подтверждение", "Удалить этого студента?"):
            self._on_delete(self.student_id)

    def _submit(self) -> None:
        if not self.student_id:
            return
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data.get(f) == DATE_PLACEHOLDER:
                data[f] = ""
        group_name = data.get("group_id", "")
        data["group_id"] = self.group_mapping.get(group_name, "")
        errors = validate_student_payload(data)
        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5]))
            return
        self._on_save(self.student_id, data)


