import tkinter as tk
from typing import Callable


class MainPage(tk.Frame):
    def __init__(self, master: tk.Misc, on_employees: Callable[[], None]) -> None:
        super().__init__(master, bg="#f3f4f6")

        title = tk.Label(
            self,
            text="Главная страница",
            font=("Segoe UI", 18, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        title.pack(pady=(28, 24))

        buttons_frame = tk.Frame(self, bg="#f3f4f6")
        buttons_frame.pack(pady=8)

        buttons = [
            ("Сотрудники", on_employees),
            ("Студенты", lambda: None),
            ("Лекарства", lambda: None),
            ("Обращение", lambda: None),
        ]

        for index, (label, command) in enumerate(buttons):
            button = tk.Button(
                buttons_frame,
                text=label,
                width=22,
                height=2,
                font=("Segoe UI", 11),
                command=command,
            )
            button.grid(row=index // 2, column=index % 2, padx=10, pady=10)
