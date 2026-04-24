import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton


class StudentsPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add: Callable[[], None],
        on_groups: Callable[[], None],
        on_back: Callable[[], None],
        on_select: Callable[[int], None],
        on_filter_changed: Callable[[str, str], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_filter_changed = on_filter_changed

        title = tk.Label(
            self,
            text="Студенты",
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

        self.filter_var = tk.StringVar(value="Все студенты")
        filter_combo = ttk.Combobox(
            filter_container,
            textvariable=self.filter_var,
            state="readonly",
            values=["Все студенты", "Просроченные", "Истекают (2 недели)"],
            width=22,
            font=("Segoe UI", 10),
        )
        filter_combo.pack(side=tk.RIGHT)
        filter_combo.bind("<<ComboboxSelected>>", self._trigger_filter)

        table_container = tk.Frame(self, bg=BG_COLOR)
        table_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        columns = ("fio", "group_name")
        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
        )
        self.table.heading("fio", text="ФИО")
        self.table.heading("group_name", text="Группа")
        self.table.column("fio", width=620, anchor=tk.W)
        self.table.column("group_name", width=240, anchor=tk.CENTER)
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

        groups_button = FlatButton(
            actions,
            primary=False,
            text="Группы",
            width=14,
            command=on_groups,
        )
        groups_button.pack(side=tk.LEFT, padx=(12, 0))

        back_button = FlatButton(
            actions,
            primary=False,
            text="Назад",
            width=14,
            command=on_back,
        )
        back_button.pack(side=tk.LEFT, padx=(12, 0))

    def set_rows(self, rows: list[tuple[int, str, str]]) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for id, fio, group_name in rows:
            self.table.insert("", tk.END, iid=str(id), values=(fio, group_name))

    def _on_double_click(self, event: tk.Event) -> None:
        self._on_open_selected()

    def _on_open_selected(self) -> None:
        selection = self.table.selection()
        if selection:
            student_id = int(selection[0])
            self.on_select(student_id)

    def _trigger_filter(self, *args: object) -> None:
        self.on_filter_changed(self.search_var.get(), self.filter_var.get())
