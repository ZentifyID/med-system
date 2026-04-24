import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton


class GroupsPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add: Callable[[], None],
        on_back: Callable[[], None],
        on_select: Callable[[int], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select

        title = tk.Label(
            self,
            text="Учебные группы",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(pady=(30, 20))

        table_container = tk.Frame(self, bg=BG_COLOR)
        table_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        columns = ("name",)
        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
        )
        self.table.heading("name", text="Название группы")
        self.table.column("name", width=860, anchor=tk.W)
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

        back_button = FlatButton(
            actions,
            primary=False,
            text="Назад",
            width=14,
            command=on_back,
        )
        back_button.pack(side=tk.LEFT, padx=(12, 0))

    def set_rows(self, rows: list[tuple[int, str]]) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for id, name in rows:
            self.table.insert("", tk.END, iid=str(id), values=(name,))

    def _on_double_click(self, event: tk.Event) -> None:
        self._on_open_selected()

    def _on_open_selected(self) -> None:
        selection = self.table.selection()
        if selection:
            group_id = int(selection[0])
            self.on_select(group_id)
