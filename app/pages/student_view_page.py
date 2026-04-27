import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, cast

import customtkinter as ctk

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton
from app.validators import DATE_FIELDS, STUDENT_FIELD_LABELS as FIELD_LABELS, allow_typed_value, validate_student_payload

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
        self.group_combobox: ttk.Combobox | None = None

        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        self.title_label = tk.Label(hdr, text="Студент", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 8))
        self.form_container = tk.Frame(card, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        for i in range(2):
            self.form_container.grid_columnconfigure(i * 2, weight=0)
            self.form_container.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(FIELDS) + 1) // 2
        for idx, (key, label) in enumerate(FIELDS):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1

            tk.Label(self.form_container, text=label, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=label_col, sticky="w", padx=(0 if block == 0 else 24, 8), pady=(0, 2))

            var = tk.StringVar()
            self.form_vars[key] = var

            val_label = tk.Label(self.form_container, textvariable=var, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
            val_label.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
            self.form_labels[key] = val_label

            if key == "group_id":
                field = ttk.Combobox(self.form_container, textvariable=var, state="readonly", font=("Segoe UI", 10))
                self.group_combobox = field
            else:
                field = ctk.CTkEntry(
                    self.form_container,
                    textvariable=var,
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    fg_color=ENTRY_BG,
                    text_color=ENTRY_FG,
                    border_color=ENTRY_BORDER,
                    corner_radius=CORNER_RADIUS,
                    height=34,
                )
                if key in DATE_FIELDS:
                    inner_entry = field._entry if hasattr(field, '_entry') else field
                    inner_entry.bind("<FocusIn>", lambda _e, k=key: self._on_date_focus_in(k))
                    inner_entry.bind("<FocusOut>", lambda _e, k=key: self._on_date_focus_out(k))
                    inner_entry.bind("<KeyPress>", lambda ev, k=key: self._on_date_keypress(ev, k))
                    inner_entry.bind("<Control-v>", lambda ev, k=key: self._on_date_paste(ev, k))
                    inner_entry.bind("<<Paste>>", lambda ev, k=key: self._on_date_paste(ev, k))
            self.form_entries[key] = field

        tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=("Segoe UI", 8, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=28)

        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=28, pady=(8, 24))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить", command=self._delete_student, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, font=ctk.CTkFont(family="Segoe UI", size=12))

        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
        self.back_button.pack(side=tk.LEFT, padx=(10, 0))

    def set_groups(self, groups: list[tuple[int, str]]) -> None:
        self.group_mapping = {name: str(id) for id, name in groups}
        self.group_mapping_reverse = {str(id): name for id, name in groups}
        if self.group_combobox:
            self.group_combobox["values"] = list(self.group_mapping.keys())
            if self.original_data:
                gid = self.original_data.get("group_id", "")
                self.form_vars["group_id"].set(self.group_mapping_reverse.get(gid, ""))

    def set_student_data(self, data: dict) -> None:
        self.student_id = int(data["id"])
        self.original_data = data.copy()
        fio = f"{data.get('last_name', '')} {data.get('first_name', '')}"
        if data.get("middle_name"): fio += f" {data['middle_name']}"
        self.title_label.config(text=f"Студент: {fio.strip()}")
        self._update_form_vars(data)
        if self.is_edit_mode: self._toggle_edit_mode()

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
            self.save_button.pack(side=tk.LEFT)
            self.cancel_button.pack(side=tk.LEFT, padx=(10, 0))
            for key, lbl in self.form_labels.items():
                gi = lbl.grid_info()
                lbl.grid_remove()
                self.form_entries[key].grid(row=gi["row"], column=gi["column"], sticky="ew", padx=(0, 8), pady=4)
        else:
            self.save_button.pack_forget()
            self.cancel_button.pack_forget()
            self.edit_button.pack(side=tk.LEFT)
            self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
            self.back_button.pack(side=tk.LEFT, padx=(10, 0))
            for key, entry in self.form_entries.items():
                entry.grid_remove()
                self.form_labels[key].grid()

    def _cancel_edit(self) -> None:
        if self.original_data: self._update_form_vars(self.original_data)
        self._toggle_edit_mode()

    def _delete_student(self) -> None:
        if self.student_id and messagebox.askyesno("Подтверждение", "Удалить этого студента?"):
            self._on_delete(self.student_id)

    def _submit(self) -> None:
        if not self.student_id: return
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data.get(f) == DATE_PLACEHOLDER: data[f] = ""
        group_name = data["group_id"]
        data["group_id"] = self.group_mapping.get(group_name, "")
        errors = validate_student_payload(data)
        if errors: messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5])); return
        self._on_save(self.student_id, data)

    def _on_date_focus_in(self, k):
        if self.form_vars[k].get() == DATE_PLACEHOLDER: self.form_vars[k].set("")

    def _on_date_focus_out(self, k):
        if not self.form_vars[k].get().strip(): self.form_vars[k].set(DATE_PLACEHOLDER)

    def _fmt(self, d):
        if len(d) <= 2: return d
        if len(d) <= 4: return f"{d[:2]}.{d[2:]}"
        return f"{d[:2]}.{d[2:4]}.{d[4:]}"

    def _d2i(self, s, i): return sum(1 for c in s[:i] if c.isdigit())
    def _i2d(self, i):
        if i <= 2: return i
        if i <= 4: return i + 1
        return i + 2
    def _digits(self, v): return "".join(c for c in v if c.isdigit())[:8]
    def _replace(self, d, s, e, r=""): return (d[:s] + r + d[e:])[:8]

    def _get_inner_entry(self, k):
        widget = self.form_entries[k]
        if isinstance(widget, ctk.CTkEntry) and hasattr(widget, '_entry'):
            return widget._entry
        return widget

    def _apply(self, k, digits, caret):
        digits = digits[:8]
        self.form_vars[k].set(self._fmt(digits))
        e = self._get_inner_entry(k)
        e.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def _on_date_keypress(self, ev, k):
        e = self._get_inner_entry(k)
        cur = e.get()
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        has_sel = e.selection_present()
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))
            en = self._d2i(cur, e.index("sel.last"))
        else:
            s = en = self._d2i(cur, e.index(tk.INSERT))
        ctrl = bool(ev.state & 0x4)
        if ctrl and ev.keysym.lower() in {"a", "c", "x"}: return None
        if ctrl and ev.keysym.lower() == "v": return self._on_date_paste(ev, k)
        if ev.keysym in {"Left", "Right", "Home", "End", "Tab", "ISO_Left_Tab", "Shift_L", "Shift_R"}: return None
        if ev.keysym == "BackSpace":
            if has_sel: return self._apply(k, self._replace(digits, s, en), s)
            if s == 0: return "break"
            return self._apply(k, self._replace(digits, s-1, s), s-1)
        if ev.keysym == "Delete":
            if has_sel: return self._apply(k, self._replace(digits, s, en), s)
            if s >= len(digits): return "break"
            return self._apply(k, self._replace(digits, s, s+1), s)
        if ev.char.isdigit():
            if len(digits) >= 8 and not has_sel: return "break"
            return self._apply(k, self._replace(digits, s, en, ev.char), s+1)
        return "break"

    def _on_date_paste(self, _ev, k):
        e = self._get_inner_entry(k)
        cur = e.get()
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        try: cb = self.clipboard_get()
        except tk.TclError: return "break"
        pd = "".join(c for c in cb if c.isdigit())
        if not pd: return "break"
        has_sel = e.selection_present()
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))
            en = self._d2i(cur, e.index("sel.last"))
        else:
            s = en = self._d2i(cur, e.index(tk.INSERT))
        nd = self._replace(digits, s, en, pd)
        return self._apply(k, nd, min(s + len(pd), len(nd)))
