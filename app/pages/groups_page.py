import tkinter as tk

from app.ui import BG_COLOR
from app.pages.shared_ui import (
    _make_section_header,
    _make_table_card,
    _make_action_bar,
)


class GroupsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_increment, on_delete=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete

        _make_section_header(self, "Учебные группы", "+ Добавить", on_add)
        tk.Frame(self, bg=BG_COLOR, height=20).pack()

        _, self.table = _make_table_card(self, ("name",), {"name": "Название группы"}, {"name": 760})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [
            ("Открыть", True, self._open_selected),
            ("Обновить курс", False, on_increment),
            ("Назад", False, on_back)
        ])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (id, name) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(id), values=(name,), tags=(tag,))

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
