import tkinter as tk
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton


class MainPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_employees: Callable[[], None],
        on_students: Callable[[], None],
        on_medicines: Callable[[], None],
        on_appeals: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)

        title = tk.Label(
            self,
            text="Главная страница",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(pady=(40, 32))

        buttons_frame = tk.Frame(self, bg=BG_COLOR)
        buttons_frame.pack(pady=8)

        buttons = [
            ("Сотрудники", on_employees),
            ("Студенты", on_students),
            ("Лекарства", on_medicines),
            ("Обращения", on_appeals),
        ]

        for index, (label, command) in enumerate(buttons):
            button = FlatButton(
                buttons_frame,
                primary=True,
                text=label,
                width=22,
                height=2,
                font=("Segoe UI", 11),
                command=command,
            )
            button.grid(row=index // 2, column=index % 2, padx=12, pady=12)
