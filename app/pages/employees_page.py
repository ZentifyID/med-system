import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_LIGHT,
    BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, sort_treeview_column
)


def _make_section_header(parent: tk.Frame, title: str, btn_text: str, btn_cmd: Callable) -> None:
    row = tk.Frame(parent, bg=BG_COLOR)
    row.pack(fill=tk.X, padx=36, pady=(32, 0))
    tk.Label(row, text=title, font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
    FlatButton(row, primary=True, text=btn_text, command=btn_cmd, height=44, width=160).pack(side=tk.RIGHT)
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 0))


def _make_search_bar(parent: tk.Frame, search_var: tk.StringVar, filter_var: tk.StringVar | None, filter_values: list[str] | None, trigger_fn: Callable) -> None:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(20, 16))

    search_entry = ctk.CTkEntry(
        bar,
        textvariable=search_var,
        font=(FONT_FAMILY, 14),
        fg_color=BG_CARD,
        text_color=TEXT_COLOR,
        border_color=ENTRY_BORDER,
        corner_radius=CORNER_RADIUS,
        placeholder_text="🔍 Поиск...",
        placeholder_text_color=TEXT_MUTED,
        height=44,
    )
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

    if filter_var and filter_values:
        combo = ctk.CTkComboBox(
            bar, variable=filter_var, state="readonly", values=filter_values, width=200,
            font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
            fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
            button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=44,
            command=trigger_fn
        )
        combo.pack(side=tk.RIGHT)


def _make_table_card(parent: tk.Frame, columns: tuple, headings: dict, widths: dict, anchors: dict | None = None) -> tuple[tk.Frame, ttk.Treeview]:
    # Modern card container for table
    card = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        border_color=BORDER,
        border_width=1,
        corner_radius=12
    )
    card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 20))

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    tv = ttk.Treeview(inner, columns=columns, show="headings")
    for col in columns:
        tv.heading(col, text=headings.get(col, col), command=lambda c=col: sort_treeview_column(tv, c, False))
        anchor = (anchors or {}).get(col, tk.W)
        tv.column(col, width=widths.get(col, 150), anchor=anchor, stretch=True)

    tv.tag_configure("odd", background=BG_CARD)
    tv.tag_configure("even", background="#F9FAFB")

    sb = ttk.Scrollbar(inner, orient=tk.VERTICAL, command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    def on_right_click(event):
        item = tv.identify_row(event.y)
        if item:
            tv.selection_set(item)
            menu = tk.Menu(parent, tearoff=0, font=(FONT_FAMILY, 10))
            if hasattr(parent, "_open_selected"):
                menu.add_command(label="Открыть / Редактировать", command=parent._open_selected)
            if hasattr(parent, "_copy_fio"):
                menu.add_command(label="Скопировать основное значение", command=parent._copy_fio)
            if hasattr(parent, "on_delete_cb"):
                menu.add_separator()
                menu.add_command(label="Удалить", command=lambda: parent.on_delete_cb(int(item)))
            menu.tk_popup(event.x_root, event.y_root)

    tv.bind("<Button-3>", on_right_click)
    
    return card, tv


def _make_action_bar(parent: tk.Frame, buttons: list[tuple[str, bool, Callable]]) -> tk.Frame:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(0, 32))
    for i, (text, primary, cmd) in enumerate(buttons):
        FlatButton(bar, primary=primary, text=text, command=cmd, height=44, width=120).pack(side=tk.LEFT, padx=(0 if i == 0 else 12, 0))
    return bar


class EmployeesPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_delete=None, on_filter_changed=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Сотрудники", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все сотрудники")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все сотрудники", "Просроченные", "Истекают (2 недели)"], self._trigger_filter)

        _, self.table = _make_table_card(self, ("fio", "affiliation", "san", "med", "flu"),
            {
                "fio": "ФИО",
                "affiliation": "Принадлежность",
                "san": "Санминимум",
                "med": "Медосмотр",
                "flu": "Флюор-я"
            },
            {
                "fio": 300,
                "affiliation": 150,
                "san": 100,
                "med": 100,
                "flu": 100
            },
            {
                "fio": tk.W,
                "affiliation": tk.CENTER,
                "san": tk.CENTER,
                "med": tk.CENTER,
                "flu": tk.CENTER
            })
    
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (id, fio, affiliation, san, med, flu) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(id), values=(fio, affiliation, san, med, flu), tags=(tag,))

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


class StudentsPage(tk.Frame):
    def __init__(self, master, on_add, on_groups, on_back, on_select, on_delete=None, on_filter_changed=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Студенты", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все студенты")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все студенты", "Просроченные", "Истекают (2 недели)"], self._trigger_filter)

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


class MedicinesPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_order=None, on_delete=None, on_filter_changed=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Лекарства", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все лекарства")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все лекарства", "Мало (<= 5)", "Истекают (2 недели)", "Просроченные"], self._trigger_filter)

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


class AppealsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_delete=None, on_filter_changed=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Обращения", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        _make_search_bar(self, self.search_var, None, None, self._trigger_filter)

        _, self.table = _make_table_card(self, ("title", "sender", "created_at"),
            {"title": "Заголовок", "sender": "От кого", "created_at": "Дата"},
            {"title": 460, "sender": 220, "created_at": 140},
            {"title": tk.W, "sender": tk.W, "created_at": tk.CENTER})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (m_id, title, sender, created_at) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(m_id), values=(title, sender, created_at), tags=(tag,))

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


class GroupsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_delete=None):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_delete_cb = on_delete

        _make_section_header(self, "Учебные группы", "+ Добавить", on_add)
        tk.Frame(self, bg=BG_COLOR, height=20).pack()

        _, self.table = _make_table_card(self, ("name",), {"name": "Название группы"}, {"name": 760})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Назад", False, on_back)])

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
