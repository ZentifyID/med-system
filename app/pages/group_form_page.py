import tkinter as tk
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton


class GroupFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[str], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self.name_var = tk.StringVar()

        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        tk.Label(hdr, text="Добавление группы", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.X, padx=28, pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=20, pady=16)

        tk.Label(inner, text="Название группы", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.name_entry = ctk.CTkEntry(
            inner, textvariable=self.name_var,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
        )
        self.name_entry.pack(fill=tk.X)

        bar = tk.Frame(self, bg=BG_COLOR)
        bar.pack(fill=tk.X, padx=28, pady=(8, 24))
        FlatButton(bar, primary=True, text="Сохранить", command=self._submit, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side=tk.LEFT)
        FlatButton(bar, primary=False, text="Отмена", command=self._on_cancel, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side=tk.LEFT, padx=(10, 0))

    def reset_form(self) -> None:
        self.name_var.set("")

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Имя группы не может быть пустым.")
            return
        self._on_save(name)
