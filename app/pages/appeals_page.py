import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton


class AppealsPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add: Callable[[], None],
        on_back: Callable[[], None],
        on_select: Callable[[int], None],
        on_filter_changed: Callable[[str], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self.on_select = on_select
        self.on_filter_changed = on_filter_changed

        title = tk.Label(
            self,
            text="Обращения",
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

        table_container = tk.Frame(self, bg=BG_COLOR)
        table_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        columns = ("title", "sender", "created_at")
        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=14,
        )
        self.table.heading("title", text="Заголовок")
        self.table.heading("sender", text="От кого")
        self.table.heading("created_at", text="Дата создания")
        
        self.table.column("title", width=500, anchor=tk.W)
        self.table.column("sender", width=220, anchor=tk.W)
        self.table.column("created_at", width=140, anchor=tk.CENTER)
        
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

    def set_rows(self, rows: list[tuple[int, str, str, str]]) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for m_id, title, sender, created_at in rows:
            self.table.insert("", tk.END, iid=str(m_id), values=(title, sender, created_at))

    def _on_double_click(self, event: tk.Event) -> None:
        self._on_open_selected()

    def _on_open_selected(self) -> None:
        selection = self.table.selection()
        if selection:
            appeal_id = int(selection[0])
            self.on_select(appeal_id)

    def _trigger_filter(self, *args: object) -> None:
        self.on_filter_changed(self.search_var.get())
