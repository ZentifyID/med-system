import tkinter as tk
from tkinter import messagebox
from typing import Callable

from app.ui import BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, FlatButton


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
        self.name_entry = tk.Entry(inner, textvariable=self.name_var, font=("Segoe UI", 11), bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
        self.name_entry.pack(fill=tk.X, ipady=6)

        bar = tk.Frame(self, bg=BG_COLOR)
        bar.pack(fill=tk.X, padx=28, pady=(8, 24))
        FlatButton(bar, primary=True, text="Сохранить", command=self._submit, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        FlatButton(bar, primary=False, text="Отмена", command=self._on_cancel, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(10, 0))

    def reset_form(self) -> None:
        self.name_var.set("")

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name: messagebox.showwarning("Ошибка", "Имя группы не может быть пустым."); return
        self._on_save(name)


class GroupViewPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[int, str], None], on_delete: Callable[[int], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self.group_id: int | None = None
        self.is_edit_mode = False
        self.original_name = ""
        self.name_var = tk.StringVar()

        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=28, pady=(24, 0))
        self.title_label = tk.Label(hdr, text="Группа", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=28, pady=(12, 16))

        card = tk.Frame(self, bg=BG_CARD)
        card.pack(fill=tk.X, padx=28, pady=(0, 16))
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=20, pady=16)

        tk.Label(inner, text="Название группы", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.name_entry = tk.Entry(inner, textvariable=self.name_var, font=("Segoe UI", 11), bg=BG_CARD, fg=TEXT_COLOR, relief=tk.FLAT, state="readonly")
        self.name_entry.pack(fill=tk.X, ipady=6)

        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=28, pady=(8, 24))

        self.edit_button      = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, font=("Segoe UI", 10))
        self.delete_button    = FlatButton(self.actions, primary=False, danger=True, text="Удалить",   command=self._delete, font=("Segoe UI", 10))
        self.back_button      = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, font=("Segoe UI", 10))
        self.save_button      = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, font=("Segoe UI", 10))
        self.cancel_edit_button = FlatButton(self.actions, primary=False, text="Отмена",  command=self._cancel_edit, font=("Segoe UI", 10))

        self._update_action_buttons()

    def set_group_data(self, data: dict) -> None:
        self.group_id = int(data["id"])
        self.original_name = data["name"]
        self.title_label.config(text=f"Группа: {self.original_name}")
        self.name_var.set(self.original_name)
        if self.is_edit_mode: self._toggle_edit_mode()
        self._update_action_buttons()

    def _update_action_buttons(self) -> None:
        for w in self.actions.winfo_children(): w.pack_forget()
        if self.is_edit_mode:
            self.save_button.pack(side=tk.LEFT)
            self.cancel_edit_button.pack(side=tk.LEFT, padx=(10, 0))
        else:
            self.edit_button.pack(side=tk.LEFT)
            self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
            self.back_button.pack(side=tk.LEFT, padx=(10, 0))

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        self._update_action_buttons()
        if self.is_edit_mode:
            self.name_entry.config(state=tk.NORMAL, bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
        else:
            self.name_entry.config(state="readonly", bg=BG_CARD, fg=TEXT_COLOR, relief=tk.FLAT, borderwidth=0)

    def _cancel_edit(self) -> None:
        self.name_var.set(self.original_name)
        self._toggle_edit_mode()

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name: messagebox.showwarning("Ошибка", "Имя группы не может быть пустым."); return
        if self.group_id: self._on_save(self.group_id, name)

    def _delete(self) -> None:
        if not self.group_id: return
        if messagebox.askyesno("Удаление", f"Удалить группу '{self.original_name}'?"):
            self._on_delete(self.group_id)
