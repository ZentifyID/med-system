import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, ENTRY_BG, ENTRY_FG, FlatButton


class AppealFormPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[dict[str, str]], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel

        self.title_var = tk.StringVar()
        self.sender_var = tk.StringVar()

        title = tk.Label(
            self,
            text="Создание обращения",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(pady=(30, 20))

        form_container = tk.Frame(self, bg=BG_COLOR)
        form_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Title
        tk.Label(
            form_container,
            text="Заголовок",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        
        tk.Entry(
            form_container,
            textvariable=self.title_var,
            font=("Segoe UI", 10),
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief=tk.SOLID,
            borderwidth=1,
        ).pack(fill=tk.X, pady=(0, 15))

        # Sender
        tk.Label(
            form_container,
            text="От кого",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.sender_combo = ttk.Combobox(
            form_container,
            textvariable=self.sender_var,
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.sender_combo.pack(fill=tk.X, pady=(0, 15))

        # Text
        tk.Label(
            form_container,
            text="Текст обращения",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.text_widget = tk.Text(
            form_container,
            font=("Segoe UI", 10),
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief=tk.SOLID,
            borderwidth=1,
            height=10,
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Actions
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

    def set_senders(self, senders: list[str]) -> None:
        self.sender_combo["values"] = senders

    def reset_form(self) -> None:
        self.title_var.set("")
        self.sender_var.set("")
        self.text_widget.delete("1.0", tk.END)

    def _submit(self) -> None:
        data = {
            "title": self.title_var.get().strip(),
            "sender": self.sender_var.get().strip(),
            "text": self.text_widget.get("1.0", tk.END).strip(),
        }
            
        errors = []
        if not data["title"]:
            errors.append("Введите заголовок.")
        if not data["sender"]:
            errors.append("Выберите отправителя.")
        if not data["text"]:
            errors.append("Введите текст обращения.")

        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors))
            return

        self._on_save(data)
