import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_LIGHT,
    BORDER, ENTRY_BG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
)


def _make_section_header(parent: tk.Frame, title: str, btn_text: str, btn_cmd: Callable) -> None:
    row = tk.Frame(parent, bg=BG_COLOR)
    row.pack(fill=tk.X, padx=36, pady=(28, 0))
    tk.Label(row, text=title, font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
    FlatButton(row, primary=True, text=btn_text, command=btn_cmd, font=ctk.CTkFont(family="Segoe UI", size=12), height=36).pack(side=tk.RIGHT)
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(12, 0))


def _make_search_bar(parent: tk.Frame, search_var: tk.StringVar, filter_var: tk.StringVar | None, filter_values: list[str] | None, trigger_fn: Callable) -> None:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(14, 12))

    search_entry = ctk.CTkEntry(
        bar,
        textvariable=search_var,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        fg_color=BG_CARD,
        text_color=TEXT_COLOR,
        border_color=ENTRY_BORDER,
        corner_radius=CORNER_RADIUS,
        placeholder_text="🔍 Поиск...",
        placeholder_text_color=TEXT_MUTED,
        height=38,
    )
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    if filter_var and filter_values:
        combo = ttk.Combobox(bar, textvariable=filter_var, state="readonly", values=filter_values, width=22, font=("Segoe UI", 10))
        combo.pack(side=tk.RIGHT)
        combo.bind("<<ComboboxSelected>>", trigger_fn)


def _make_table_card(parent: tk.Frame, columns: tuple, headings: dict, widths: dict, anchors: dict | None = None) -> tuple[tk.Frame, ttk.Treeview]:
    # Card with 1px border
    outer = tk.Frame(parent, bg=BORDER)
    outer.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 14))

    card = tk.Frame(outer, bg=BG_CARD)
    card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    tv = ttk.Treeview(card, columns=columns, show="headings")
    for col in columns:
        tv.heading(col, text=headings.get(col, col))
        anchor = (anchors or {}).get(col, tk.W)
        tv.column(col, width=widths.get(col, 150), anchor=anchor, stretch=True)

    tv.tag_configure("odd", background=BG_CARD)
    tv.tag_configure("even", background="#F9FAFB")

    sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    return outer, tv


def _make_action_bar(parent: tk.Frame, buttons: list[tuple[str, bool, Callable]]) -> tk.Frame:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(0, 28))
    for i, (text, primary, cmd) in enumerate(buttons):
        FlatButton(bar, primary=primary, text=text, command=cmd, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))
    return bar


class EmployeesPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_filter_changed):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Сотрудники", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все сотрудники")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все сотрудники", "Просроченные", "Истекают (2 недели)"], self._trigger_filter)

        _, self.table = _make_table_card(self, ("fio", "affiliation"),
            {"fio": "ФИО", "affiliation": "Принадлежность"},
            {"fio": 560, "affiliation": 200},
            {"fio": tk.W, "affiliation": tk.CENTER})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (id, fio, affiliation) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(id), values=(fio, affiliation), tags=(tag,))

    def _open_selected(self):
        sel = self.table.selection()
        if sel:
            self.on_select(int(sel[0]))

    def _trigger_filter(self, *args):
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())


class StudentsPage(tk.Frame):
    def __init__(self, master, on_add, on_groups, on_back, on_select, on_filter_changed):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_filter_changed = on_filter_changed

        _make_section_header(self, "Студенты", "+ Добавить", on_add)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        self.filter_var = tk.StringVar(value="Все студенты")
        _make_search_bar(self, self.search_var, self.filter_var, ["Все студенты", "Просроченные", "Истекают (2 недели)"], self._trigger_filter)

        _, self.table = _make_table_card(self, ("fio", "group_name"),
            {"fio": "ФИО", "group_name": "Группа"},
            {"fio": 560, "group_name": 200},
            {"fio": tk.W, "group_name": tk.CENTER})
        self.table.bind("<Double-1>", lambda e: self._open_selected())

        _make_action_bar(self, [("Открыть", True, self._open_selected), ("Группы", False, on_groups), ("Назад", False, on_back)])

    def set_rows(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for i, (id, fio, group_name) in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=str(id), values=(fio, group_name), tags=(tag,))

    def _open_selected(self):
        sel = self.table.selection()
        if sel:
            self.on_select(int(sel[0]))

    def _trigger_filter(self, *args):
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())


class MedicinesPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_order, on_filter_changed):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
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

    def _trigger_filter(self, *args):
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())


class AppealsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select, on_filter_changed):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
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

    def _trigger_filter(self, *args):
        self.on_filter_changed(self.search_var.get())


class GroupsPage(tk.Frame):
    def __init__(self, master, on_add, on_back, on_select):
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select

        _make_section_header(self, "Учебные группы", "+ Добавить", on_add)
        tk.Frame(self, bg=BG_COLOR, height=14).pack()

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
