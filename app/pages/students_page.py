import tkinter as tk

from app.ui import BG_COLOR
from app.pages.shared_ui import (
    _make_section_header,
    _make_search_bar,
    _make_table_card,
    _make_action_bar,
)


class StudentsPage(tk.Frame):
    def __init__(self, master, on_add, on_groups, on_back, on_select, on_delete=None, on_filter_changed=None, search_icon=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Студенты", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все студенты")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все студенты", "Просроченные", "Истекают (2 недели)"], self._trigger_filter, search_icon=search_icon)

        _, self.table = _make_table_card(self, ("fio", "group_name", "san", "med", "flu"),
            {
                "fio": "ФИО",
                "group_name": "Группа",
                "san": "Санминимум",
                "med": "Медосмотр",
                "flu": "Флюор-я"
            },
            {
                "fio": 300,
                "group_name": 150,
                "san": 100,
                "med": 100,
                "flu": 100
            },
            {
                "fio": tk.W,
                "group_name": tk.CENTER,
                "san": tk.CENTER,
                "med": tk.CENTER,
                "flu": tk.CENTER
            })
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Группы", False, on_groups), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (id, fio, group_name, san, med, flu) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(id), values=(fio, group_name, san, med, flu), tags=(tag,))

    def _open_selected(self):
        sel = self.table.selection()
        if sel:
            self.on_select(int(sel[0]))

    def _copy_fio(self):
        sel = self.table.selection()
        if sel:
            vals = self.table.item(sel[0], "values")
            if vals:
                self.clipboard_clear()
                self.clipboard_append(vals[0])

    def _trigger_filter(self, *args):
        self.config(cursor="watch")
        self.update_idletasks()
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())
        self.config(cursor="")
