import tkinter as tk
from tkinter import ttk
from typing import Callable


class EmployeesPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add: Callable[[], None],
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master, bg="#f3f4f6")

        title = tk.Label(
            self,
            text="Сотрудники",
            font=("Segoe UI", 18, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        title.pack(pady=(20, 12))

        table_container = tk.Frame(self, bg="#f3f4f6")
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("fio", "affiliation")
        self.employees_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
        )
        self.employees_table.heading("fio", text="ФИО")
        self.employees_table.heading("affiliation", text="Принадлежность")
        self.employees_table.column("fio", width=620, anchor=tk.W)
        self.employees_table.column("affiliation", width=240, anchor=tk.CENTER)

        y_scroll = ttk.Scrollbar(
            table_container, orient=tk.VERTICAL, command=self.employees_table.yview
        )
        self.employees_table.configure(yscrollcommand=y_scroll.set)

        self.employees_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        actions = tk.Frame(self, bg="#f3f4f6")
        actions.pack(fill=tk.X, padx=20, pady=(0, 20))

        add_button = tk.Button(
            actions,
            text="Добавить",
            width=14,
            font=("Segoe UI", 10),
            command=on_add,
        )
        add_button.pack(side=tk.LEFT)

        back_button = tk.Button(
            actions,
            text="Назад",
            width=14,
            font=("Segoe UI", 10),
            command=on_back,
        )
        back_button.pack(side=tk.LEFT, padx=(10, 0))

    def set_rows(self, rows: list[tuple[str, str]]) -> None:
        for item in self.employees_table.get_children():
            self.employees_table.delete(item)

        for fio, affiliation in rows:
            self.employees_table.insert("", tk.END, values=(fio, affiliation))
