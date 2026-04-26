import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, cast

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, ACCENT, BORDER,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, DANGER, FlatButton,
)
from app.validators import (
    AFFILIATION_UI_VALUES, DATE_FIELDS, FIELD_LABELS,
    allow_typed_value, normalize_affiliation, validate_employee_payload,
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


class EmployeeViewPage(tk.Frame):
    def __init__(self, master: tk.Misc, on_save: Callable[[int, dict], None], on_delete: Callable[[int], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")

        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Widget] = {}
        self.form_labels: dict[str, tk.Label] = {}
        self.original_data: dict | None = None
        self.employee_id: int | None = None
        self.is_edit_mode = False

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        self.title_label = tk.Label(hdr, text="Сотрудник", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        # Card
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
            lpad = (0 if block == 0 else 24, 8)

            tk.Label(self.form_container, text=label, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=label_col, sticky="w", padx=lpad, pady=(0, 2))

            var = tk.StringVar()
            self.form_vars[key] = var

            # View label
            val_label = tk.Label(self.form_container, textvariable=var, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
            val_label.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
            self.form_labels[key] = val_label

            # Edit widget
            if key == "affiliation":
                field = ttk.Combobox(self.form_container, textvariable=var, state="readonly", values=AFFILIATION_UI_VALUES, font=("Segoe UI", 10))
            else:
                field = tk.Entry(self.form_container, textvariable=var, font=("Segoe UI", 10),
                                 validate="key", validatecommand=self._validate_cmd,
                                 name=f"field_{key}", bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
                if key in DATE_FIELDS:
                    field.bind("<FocusIn>", lambda _e, k=key: self._on_date_focus_in(k))
                    field.bind("<FocusOut>", lambda _e, k=key: self._on_date_focus_out(k))
                    field.bind("<KeyPress>", lambda ev, k=key: self._on_date_keypress(ev, k))
                    field.bind("<Control-v>", lambda ev, k=key: self._on_date_paste(ev, k))
                    field.bind("<<Paste>>", lambda ev, k=key: self._on_date_paste(ev, k))
            self.form_entries[key] = field

        tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=("Segoe UI", 8, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=28)

        # Actions
        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=28, pady=(8, 24))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, font=("Segoe UI", 10))
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить",   command=self._delete_employee, font=("Segoe UI", 10))
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, font=("Segoe UI", 10))
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, font=("Segoe UI", 10))
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, font=("Segoe UI", 10))

        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
        self.back_button.pack(side=tk.LEFT, padx=(10, 0))

    def set_employee_data(self, data: dict) -> None:
        self.employee_id = int(data["id"])
        self.original_data = data.copy()
        fio = f"{data.get('last_name', '')} {data.get('first_name', '')}"
        if data.get("middle_name"): fio += f" {data['middle_name']}"
        self.title_label.config(text=f"Сотрудник: {fio.strip()}")
        self._update_form_vars(data)
        if self.is_edit_mode: self._toggle_edit_mode()

    def _update_form_vars(self, data: dict) -> None:
        for key, var in self.form_vars.items():
            value = data.get(key, "")
            if key == "affiliation":
                var.set(AFFILIATION_UI_VALUES[0] if value == "основной" else AFFILIATION_UI_VALUES[1])
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

    def _delete_employee(self) -> None:
        if self.employee_id and messagebox.askyesno("Подтверждение", "Удалить этого сотрудника?"):
            self._on_delete(self.employee_id)

    def _validate_input(self, proposed: str, widget_path: str) -> bool:
        key = widget_path.split(".")[-1].replace("field_", "")
        return allow_typed_value(key, proposed) if key in self.form_vars else True

    def _submit(self) -> None:
        if not self.employee_id: return
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data[f] == DATE_PLACEHOLDER: data[f] = ""
        data["affiliation"] = normalize_affiliation(data["affiliation"])
        errors = validate_employee_payload(data)
        if errors: messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5])); return
        self._on_save(self.employee_id, data)

    # ── Date helpers ──────────────────────────────────────────────────────────
    def _on_date_focus_in(self, k):
        if self.form_vars[k].get() == DATE_PLACEHOLDER: self.form_vars[k].set("")

    def _on_date_focus_out(self, k):
        if not self.form_vars[k].get().strip(): self.form_vars[k].set(DATE_PLACEHOLDER)

    def _fmt(self, digits):
        if len(digits) <= 2: return digits
        if len(digits) <= 4: return f"{digits[:2]}.{digits[2:]}"
        return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"

    def _d2i(self, display, idx): return sum(1 for c in display[:idx] if c.isdigit())
    def _i2d(self, i):
        if i <= 2: return i
        if i <= 4: return i + 1
        return i + 2

    def _digits(self, v): return "".join(c for c in v if c.isdigit())[:8]
    def _replace(self, digits, s, e, r=""): return (digits[:s] + r + digits[e:])[:8]

    def _apply(self, k, digits, caret):
        digits = digits[:8]
        self.form_vars[k].set(self._fmt(digits))
        e = cast(tk.Entry, self.form_entries[k])
        e.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def _on_date_keypress(self, ev, k):
        e = cast(tk.Entry, self.form_entries[k])
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
        e = cast(tk.Entry, self.form_entries[k])
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
