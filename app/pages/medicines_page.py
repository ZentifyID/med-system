import tkinter as tk

from app.ui import BG_COLOR
from app.pages.shared_ui import (
    _make_section_header,
    _make_search_bar,
    _make_table_card,
    _make_action_bar,
)


class MedicinesPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_order=None, on_delete=None, on_filter_changed=None, search_icon=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Лекарства", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все лекарства")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все лекарства", "Мало (<= 5)", "Истекают (2 недели)", "Просроченные"], self._trigger_filter, search_icon=search_icon)

        _, self.table = _make_table_card(self, ("name", "quantity", "unit", "expiration_date"),
            {"name": "Название", "quantity": "Кол-во", "unit": "Ед. изм.", "expiration_date": "Срок годности"},
            {"name": 380, "quantity": 90, "unit": 130, "expiration_date": 160},
            {"name": tk.W, "quantity": tk.CENTER, "unit": tk.W, "expiration_date": tk.CENTER})

        self.table.tag_configure("expiring", foreground="#D97706")
        self.table.tag_configure("low_qty", foreground="#DC2626")
        self.table.tag_configure("expiring_low", foreground="#DC2626")
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Заказать", False, on_order), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, row in enumerate(rows):
            m_id, name, qty, unit, exp_date, is_expiring, is_low_qty = row
            base_tag = "odd" if i % 2 == 0 else "even"
            if is_expiring and is_low_qty:
                color_tag = "expiring_low"
            elif is_expiring:
                color_tag = "expiring"
            elif is_low_qty:
                color_tag = "low_qty"
            else:
                color_tag = base_tag
            self.table.insert("", tk.END, iid=str(m_id), values=(name, qty, unit, exp_date), tags=(color_tag,))

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
