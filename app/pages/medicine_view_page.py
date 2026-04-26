import tkinter as tk
from tkinter import messagebox
from typing import Callable

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, FlatButton

DATE_PLACEHOLDER = "__.__.____"
MED_FIELDS = [("name", "Название препарата"), ("quantity", "Количество"), ("unit", "Единицы измерения"), ("expiration_date", "Срок годности")]


class MedicineViewPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[int, dict], None], on_delete: Callable[[int], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")

        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Widget] = {}
        self.form_labels: dict[str, tk.Label] = {}
        self.original_data: dict | None = None
        self.medicine_id: int | None = None
        self.is_edit_mode = False

        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        self.title_label = tk.Label(hdr, text="Лекарство", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 8))
        self.form_container = tk.Frame(card, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)
        self.form_container.grid_columnconfigure(1, weight=1)

        for row, (key, label) in enumerate(MED_FIELDS):
            tk.Label(self.form_container, text=label, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(
                row=row, column=0, sticky="w", padx=(0, 16), pady=(0, 2))
            var = tk.StringVar()
            self.form_vars[key] = var

            val_label = tk.Label(self.form_container, textvariable=var, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
            val_label.grid(row=row, column=1, sticky="ew", pady=4)
            self.form_labels[key] = val_label

            field = tk.Entry(self.form_container, textvariable=var, font=("Segoe UI", 10),
                             validate="key", validatecommand=self._validate_cmd,
                             name=f"field_{key}", bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
            if key == "expiration_date":
                field.bind("<FocusIn>", lambda _e, k=key: self._date_focus_in(k))
                field.bind("<FocusOut>", lambda _e, k=key: self._date_focus_out(k))
                field.bind("<KeyPress>", lambda ev, k=key: self._date_keypress(ev, k))
                field.bind("<Control-v>", lambda ev, k=key: self._date_paste(ev, k))
                field.bind("<<Paste>>", lambda ev, k=key: self._date_paste(ev, k))
            self.form_entries[key] = field

        tk.Label(self, text="Формат даты: ДД.ММ.ГГГГ", font=("Segoe UI", 8, "italic"), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=28)

        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=28, pady=(8, 24))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, font=("Segoe UI", 10))
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить",   command=self._delete, font=("Segoe UI", 10))
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, font=("Segoe UI", 10))
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, font=("Segoe UI", 10))
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, font=("Segoe UI", 10))

        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
        self.back_button.pack(side=tk.LEFT, padx=(10, 0))

    def set_medicine_data(self, data: dict) -> None:
        self.medicine_id = int(data["id"])
        self.original_data = data.copy()
        self.title_label.config(text=f"Лекарство: {data.get('name', '')}")
        for key, var in self.form_vars.items():
            var.set(data.get(key, ""))
        if self.is_edit_mode: self._toggle_edit_mode()

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.pack_forget(); self.delete_button.pack_forget(); self.back_button.pack_forget()
            self.save_button.pack(side=tk.LEFT)
            self.cancel_button.pack(side=tk.LEFT, padx=(10, 0))
            for key, lbl in self.form_labels.items():
                gi = lbl.grid_info(); lbl.grid_remove()
                self.form_entries[key].grid(row=gi["row"], column=gi["column"], sticky="ew", padx=(0, 8), pady=4)
        else:
            self.save_button.pack_forget(); self.cancel_button.pack_forget()
            self.edit_button.pack(side=tk.LEFT)
            self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
            self.back_button.pack(side=tk.LEFT, padx=(10, 0))
            for key, entry in self.form_entries.items():
                entry.grid_remove(); self.form_labels[key].grid()

    def _cancel_edit(self) -> None:
        if self.original_data:
            for k, v in self.form_vars.items(): v.set(self.original_data.get(k, ""))
        self._toggle_edit_mode()

    def _delete(self) -> None:
        if self.medicine_id and messagebox.askyesno("Подтверждение", "Удалить это лекарство?"):
            self._on_delete(self.medicine_id)

    def _validate_input(self, proposed: str, widget_path: str) -> bool:
        key = widget_path.split(".")[-1].replace("field_", "")
        if key == "quantity" and proposed and not proposed.isdigit(): return False
        return True

    def _submit(self) -> None:
        if not self.medicine_id: return
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        if data["expiration_date"] == DATE_PLACEHOLDER: data["expiration_date"] = ""
        errors = []
        if not data["name"]: errors.append("Введите название.")
        if not data["quantity"]: errors.append("Введите количество.")
        elif not data["quantity"].isdigit(): errors.append("Количество должно быть числом.")
        if not data["unit"]: errors.append("Введите единицы измерения.")
        if not data["expiration_date"] or len(data["expiration_date"]) != 10: errors.append("Введите срок годности (ДД.ММ.ГГГГ).")
        if errors: messagebox.showwarning("Ошибка", "\n".join(errors)); return
        self._on_save(self.medicine_id, data)

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
        e.icursor(self._i2d(max(0, min(caret, len(digits)))))  # type: ignore
        return "break"

    def _date_keypress(self, ev, k):
        e = self.form_entries[k]
        cur = e.get()  # type: ignore
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        has_sel = e.selection_present()  # type: ignore
        s = en = self._d2i(cur, e.index(tk.INSERT))  # type: ignore
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))  # type: ignore
            en = self._d2i(cur, e.index("sel.last"))  # type: ignore
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
        cur = e.get()  # type: ignore
        if cur == DATE_PLACEHOLDER: cur = ""
        digits = self._digits(cur)
        try: cb = self.clipboard_get()
        except tk.TclError: return "break"
        pd = "".join(c for c in cb if c.isdigit())
        if not pd: return "break"
        has_sel = e.selection_present()  # type: ignore
        s = en = self._d2i(cur, e.index(tk.INSERT))  # type: ignore
        if has_sel:
            s = self._d2i(cur, e.index("sel.first"))  # type: ignore
            en = self._d2i(cur, e.index("sel.last"))  # type: ignore
        nd = self._replace(digits, s, en, pd)
        return self._apply(k, nd, min(s + len(pd), len(nd)))
