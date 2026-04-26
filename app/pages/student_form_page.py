import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, FlatButton
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


class StudentFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")
        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Entry] = {}
        self.group_mapping: dict[str, str] = {}
        self.group_combobox: ttk.Combobox | None = None

        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        tk.Label(hdr, text="Добавление студента", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        for i in range(2):
            inner.grid_columnconfigure(i * 2, weight=0)
            inner.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(FIELDS) + 1) // 2
        for idx, (key, label) in enumerate(FIELDS):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1
            lpad = (0 if block == 0 else 24, 8)

            tk.Label(inner, text=label, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=label_col, sticky="w", padx=lpad, pady=(0, 2))

            var = tk.StringVar()
            self.form_vars[key] = var

            if key == "group_id":
                cb = ttk.Combobox(inner, textvariable=var, state="readonly", font=("Segoe UI", 10))
                cb.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
                self.group_combobox = cb
            else:
                entry = tk.Entry(inner, textvariable=var, font=("Segoe UI", 10),
                                 validate="key", validatecommand=self._validate_cmd,
                                 name=f"field_{key}", bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
                entry.grid(row=row, column=input_col, sticky="ew", padx=(0, 8 if block == 0 else 0), pady=4)
                self.form_entries[key] = entry
                if key in DATE_FIELDS:
                    entry.bind("<FocusIn>", lambda _e, k=key: self._on_date_focus_in(k))
                    entry.bind("<FocusOut>", lambda _e, k=key: self._on_date_focus_out(k))
                    entry.bind("<KeyPress>", lambda ev, k=key: self._on_date_keypress(ev, k))
                    entry.bind("<Control-v>", lambda ev, k=key: self._on_date_paste(ev, k))
                    entry.bind("<<Paste>>", lambda ev, k=key: self._on_date_paste(ev, k))

        tk.Label(self, text="Формат дат: ДД.ММ.ГГГГ", font=("Segoe UI", 8, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=28)
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=28, pady=(8, 24))
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        FlatButton(actions, primary=False, text="Отмена", command=self._on_cancel, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

    def set_groups(self, groups: list[tuple[int, str]]) -> None:
        self.group_mapping = {name: str(id) for id, name in groups}
        if self.group_combobox:
            self.group_combobox["values"] = list(self.group_mapping.keys())
            if self.group_combobox["values"]:
                self.form_vars["group_id"].set(self.group_combobox["values"][0])

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            if key in DATE_FIELDS:
                var.set(DATE_PLACEHOLDER)
            elif key != "group_id":
                var.set("")

    def _validate_input(self, proposed: str, widget_path: str) -> bool:
        key = widget_path.split(".")[-1].replace("field_", "")
        return allow_typed_value(key, proposed) if key in self.form_vars else True

    def _submit(self) -> None:
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        for f in DATE_FIELDS:
            if data.get(f) == DATE_PLACEHOLDER: data[f] = ""
        group_name = data["group_id"]
        data["group_id"] = self.group_mapping.get(group_name, "")
        errors = validate_student_payload(data)
        if errors: messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5])); return
        self._on_save(data)

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

    def _apply(self, k, digits, caret):
        digits = digits[:8]
        self.form_vars[k].set(self._fmt(digits))
        e = self.form_entries[k]
        e.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def _on_date_keypress(self, ev, k):
        e = self.form_entries[k]
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
        e = self.form_entries[k]
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
