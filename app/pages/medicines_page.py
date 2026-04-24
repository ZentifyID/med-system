import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton


class MedicinesPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add: Callable[[], None],
        on_back: Callable[[], None],
        on_select: Callable[[int], None],
        on_order: Callable[[], None],
        on_filter_changed: Callable[[str, str], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_filter_changed = on_filter_changed

        title = tk.Label(
            self,
            text="Лекарства",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(pady=(30, 20))

        filter_container = tk.Frame(self, bg=BG_COLOR)
        filter_container.pack(fill=tk.X, padx=30, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)
        
        search_entry = tk.Entry(
            filter_container,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            relief=tk.SOLID,
            borderwidth=1,
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.filter_var = tk.StringVar(value="Все лекарства")
        filter_combo = ttk.Combobox(
            filter_container,
            textvariable=self.filter_var,
            state="readonly",
            values=["Все лекарства", "Мало (<= 5)", "Истекают (2 недели)", "Просроченные"],
            width=22,
            font=("Segoe UI", 10),
        )
        filter_combo.pack(side=tk.RIGHT)
        filter_combo.bind("<<ComboboxSelected>>", self._trigger_filter)

        table_container = tk.Frame(self, bg=BG_COLOR)
        table_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        columns = ("name", "quantity", "unit", "expiration_date")
        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
        )
        self.table.heading("name", text="Название")
        self.table.heading("quantity", text="Кол-во")
        self.table.heading("unit", text="Ед. изм.")
        self.table.heading("expiration_date", text="Срок годности")
        
        self.table.column("name", width=420, anchor=tk.W)
        self.table.column("quantity", width=100, anchor=tk.CENTER)
        self.table.column("unit", width=140, anchor=tk.W)
        self.table.column("expiration_date", width=200, anchor=tk.CENTER)
        
        # Highlight tags
        self.table.tag_configure("expiring", foreground="#e74c3c") # Redish color
        self.table.tag_configure("low_qty", foreground="#e67e22") # Orange color
        self.table.tag_configure("expiring_low", foreground="#c0392b") # Darker red if both

        self.table.bind("<Double-1>", self._on_double_click)

        y_scroll = ttk.Scrollbar(
            table_container, orient=tk.VERTICAL, command=self.table.yview
        )
        self.table.configure(yscrollcommand=y_scroll.set)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=30, pady=(10, 30))

        add_button = FlatButton(
            actions,
            primary=True,
            text="Добавить",
            width=14,
            command=on_add,
        )
        add_button.pack(side=tk.LEFT)

        open_button = FlatButton(
            actions,
            primary=True,
            text="Открыть",
            width=14,
            command=self._on_open_selected,
        )
        open_button.pack(side=tk.LEFT, padx=(12, 0))

        order_button = FlatButton(
            actions,
            primary=False,
            text="Заказать",
            width=14,
            command=on_order,
        )
        order_button.pack(side=tk.LEFT, padx=(12, 0))

        back_button = FlatButton(
            actions,
            primary=False,
            text="Назад",
            width=14,
            command=on_back,
        )
        back_button.pack(side=tk.LEFT, padx=(12, 0))

    def set_rows(self, rows: list[tuple[int, str, int, str, str, bool, bool]]) -> None:
        # id, name, quantity, unit, exp_date, is_expiring, is_low_qty
        for item in self.table.get_children():
            self.table.delete(item)

        for row in rows:
            m_id, name, qty, unit, exp_date, is_expiring, is_low_qty = row
            tags = ()
            if is_expiring and is_low_qty:
                tags = ("expiring_low",)
            elif is_expiring:
                tags = ("expiring",)
            elif is_low_qty:
                tags = ("low_qty",)

            self.table.insert("", tk.END, iid=str(m_id), values=(name, qty, unit, exp_date), tags=tags)

    def _on_double_click(self, event: tk.Event) -> None:
        self._on_open_selected()

    def _on_open_selected(self) -> None:
        selection = self.table.selection()
        if selection:
            medicine_id = int(selection[0])
            self.on_select(medicine_id)

    def _trigger_filter(self, *args: object) -> None:
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())
