import tkinter as tk
from tkinter import messagebox
from typing import Callable

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, FlatButton

DATE_PLACEHOLDER = "__.__.____"
MED_FIELDS = [("name", "Название препарата"), ("quantity", "Количество"), ("unit", "Единицы измерения"), ("expiration_date", "Срок годности")]


def _make_header(parent, title):
    h = tk.Frame(parent, bg=BG_COLOR)
    h.pack(fill=tk.X, padx=28, pady=(24, 0))
    tk.Label(h, text=title, font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))


class MedicineFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")
        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Entry] = {}

        _make_header(self, "Добавление лекарства")

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)
        inner.grid_columnconfigure(1, weight=1)

        for row, (key, label) in enumerate(MED_FIELDS):
            tk.Label(inner, text=label, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=0, sticky="w", padx=(0, 16), pady=(0, 2))
            var = tk.StringVar()
            self.form_vars[key] = var
            entry = tk.Entry(inner, textvariable=var, font=("Segoe UI", 10),
                             validate="key", validatecommand=self._validate_cmd,
                             name=f"field_{key}", bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.form_entries[key] = entry
            if key == "expiration_date":
                entry.bind("<FocusIn>", lambda _e, k=key: self._date_focus_in(k))
                entry.bind("<FocusOut>", lambda _e, k=key: self._date_focus_out(k))
                entry.bind("<KeyPress>", lambda ev, k=key: self._date_keypress(ev, k))
                entry.bind("<Control-v>", lambda ev, k=key: self._date_paste(ev, k))
                entry.bind("<<Paste>>", lambda ev, k=key: self._date_paste(ev, k))

        tk.Label(self, text="Формат даты: ДД.ММ.ГГГГ", font=("Segoe UI", 8, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=28)
        bar = tk.Frame(self, bg=BG_COLOR)
        bar.pack(fill=tk.X, padx=28, pady=(8, 24))
        FlatButton(bar, primary=True, text="Сохранить", command=self._submit, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        FlatButton(bar, primary=False, text="Отмена", command=self._on_cancel, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            var.set(DATE_PLACEHOLDER if key == "expiration_date" else "")

    def _validate_input(self, proposed: str, widget_path: str) -> bool:
        key = widget_path.split(".")[-1].replace("field_", "")
        if key == "quantity" and proposed and not proposed.isdigit(): return False
        return True

    def _submit(self) -> None:
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        if data["expiration_date"] == DATE_PLACEHOLDER: data["expiration_date"] = ""
        errors = []
        if not data["name"]: errors.append("Введите название.")
        if not data["quantity"]: errors.append("Введите количество.")
        elif not data["quantity"].isdigit(): errors.append("Количество должно быть числом.")
        if not data["unit"]: errors.append("Введите единицы измерения.")
        if not data["expiration_date"] or len(data["expiration_date"]) != 10: errors.append("Введите срок годности (ДД.ММ.ГГГГ).")
        if errors: messagebox.showwarning("Ошибка", "\n".join(errors)); return
        self._on_save(data)

    def _date_focus_in(self, k):
        if self.form_vars[k].get() == DATE_PLACEHOLDER: self.form_vars[k].set("")

    def _date_focus_out(self, k):
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
        self.form_vars[k].set(self._fmt(digits[:8]))
        e = self.form_entries[k]
        e.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def _date_keypress(self, ev, k):
        e = self.form_entries[k]
        cur = e.get()
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        has_sel = e.selection_present()
        s = en = self._d2i(cur, e.index(tk.INSERT))
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))
            en = self._d2i(cur, e.index("sel.last"))
        ctrl = bool(ev.state & 0x4)
        if ctrl and ev.keysym.lower() in {"a", "c", "x"}: return None
        if ctrl and ev.keysym.lower() == "v": return self._date_paste(ev, k)
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

    def _date_paste(self, _ev, k):
        e = self.form_entries[k]
        cur = e.get()
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        try: cb = self.clipboard_get()
        except tk.TclError: return "break"
        pd = "".join(c for c in cb if c.isdigit())
        if not pd: return "break"
        has_sel = e.selection_present()
        s = en = self._d2i(cur, e.index(tk.INSERT))
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))
            en = self._d2i(cur, e.index("sel.last"))
        nd = self._replace(digits, s, en, pd)
        return self._apply(k, nd, min(s + len(pd), len(nd)))
