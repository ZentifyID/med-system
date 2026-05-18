import tkinter as tk

from app.ui import BG_COLOR
from app.pages.shared_ui import (
    _make_section_header,
    _make_search_bar,
    _make_table_card,
    _make_action_bar,
)


class AppealsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_delete=None, on_filter_changed=None, search_icon=None,
                 fetch_icd_cb=None, insert_icd_cb=None, update_icd_cb=None, delete_icd_cb=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed
        self.search_icon = search_icon
        self.fetch_icd_cb = fetch_icd_cb
        self.insert_icd_cb = insert_icd_cb
        self.update_icd_cb = update_icd_cb
        self.delete_icd_cb = delete_icd_cb

        _make_section_header(self, "Обращения", "+ Добавить", on_add, "Справочник МКБ", self._open_icd_reference)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        _make_search_bar(self, self.search_var, None, None, self._trigger_filter, search_icon=search_icon)

        _, self.table = _make_table_card(self, ("number", "created_at", "sender", "complaints"),
            {"number": "№", "created_at": "Дата", "sender": "ФИО", "complaints": "Жалобы"},
            {"number": 60, "created_at": 100, "sender": 250, "complaints": 350},
            {"number": tk.CENTER, "created_at": tk.CENTER, "sender": tk.W, "complaints": tk.W})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (m_id, number, created_at, sender, complaints) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(m_id), values=(number, created_at, sender, complaints), tags=(tag,))

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
        self.on_filter_changed(self.search_var.get())
        self.config(cursor="")

    def _open_icd_reference(self):
        from app.pages.icd_reference_dialog import ICDReferenceDialog
        ICDReferenceDialog(
            self.winfo_toplevel(),
            fetch_cb=self.fetch_icd_cb,
            insert_cb=self.insert_icd_cb,
            update_cb=self.update_icd_cb,
            delete_cb=self.delete_icd_cb,
            search_icon=self.search_icon
        )
