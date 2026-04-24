import tkinter as tk
from tkinter import messagebox
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, FlatButton


class GroupFormPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[str], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel

        self.title_label = tk.Label(
            self,
            text="Добавление группы",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self.title_label.pack(pady=(30, 20))

        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        label = tk.Label(
            form_frame,
            text="Название группы",
            font=("Segoe UI", 11),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor=tk.W,
        )
        label.pack(fill=tk.X, pady=(0, 5))

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            form_frame,
            textvariable=self.name_var,
            font=("Segoe UI", 11),
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.name_entry.pack(fill=tk.X, pady=(0, 15), ipady=4)

        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=30, pady=(10, 30))

        save_button = FlatButton(
            actions,
            primary=True,
            text="Сохранить",
            width=14,
            command=self._submit,
        )
        save_button.pack(side=tk.LEFT)

        cancel_button = FlatButton(
            actions,
            primary=False,
            text="Отмена",
            width=14,
            command=self._on_cancel,
        )
        cancel_button.pack(side=tk.LEFT, padx=(12, 0))

    def reset_form(self) -> None:
        self.name_var.set("")

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Имя группы не может быть пустым.")
            return

        self._on_save(name)
