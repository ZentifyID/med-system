import tkinter as tk
from tkinter import messagebox
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, FlatButton


class GroupViewPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[int, str], None],
        on_delete: Callable[[int], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel

        self.group_id: int | None = None
        self.is_edit_mode = False
        self.original_name = ""

        self.title_label = tk.Label(
            self,
            text="Группа",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self.title_label.pack(pady=(30, 20))

        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        self.name_label_widget = tk.Label(
            form_frame,
            text="Название группы",
            font=("Segoe UI", 11),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor=tk.W,
        )
        self.name_label_widget.pack(fill=tk.X, pady=(0, 5))

        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            form_frame,
            textvariable=self.name_var,
            font=("Segoe UI", 11),
            bg=BG_COLOR, # It will be updated based on state
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            state="readonly",
        )
        self.name_entry.pack(fill=tk.X, pady=(0, 15), ipady=4)

        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=30, pady=(10, 30))

        self.edit_button = FlatButton(
            self.actions,
            primary=True,
            text="Изменить",
            width=14,
            command=self._toggle_edit_mode,
        )

        self.delete_button = FlatButton(
            self.actions,
            primary=False,
            text="Удалить",
            width=14,
            command=self._delete,
        )

        self.back_button = FlatButton(
            self.actions,
            primary=False,
            text="Назад",
            width=14,
            command=self._on_cancel,
        )

        self.save_button = FlatButton(
            self.actions,
            primary=True,
            text="Сохранить",
            width=14,
            command=self._submit,
        )

        self.cancel_edit_button = FlatButton(
            self.actions,
            primary=False,
            text="Отмена",
            width=14,
            command=self._cancel_edit,
        )

    def set_group_data(self, data: dict[str, str]) -> None:
        self.group_id = int(data["id"])
        self.original_name = data["name"]
        self.title_label.config(text=f"Группа: {self.original_name}")
        self.name_var.set(self.original_name)
        
        if self.is_edit_mode:
            self._toggle_edit_mode()
        self._update_action_buttons()

    def _update_action_buttons(self) -> None:
        for widget in self.actions.winfo_children():
            widget.pack_forget()

        if self.is_edit_mode:
            self.save_button.pack(side=tk.LEFT)
            self.cancel_edit_button.pack(side=tk.LEFT, padx=(12, 0))
        else:
            self.edit_button.pack(side=tk.LEFT)
            self.delete_button.pack(side=tk.LEFT, padx=(12, 0))
            self.back_button.pack(side=tk.LEFT, padx=(12, 0))

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        self._update_action_buttons()
        
        if self.is_edit_mode:
            self.name_entry.config(
                state=tk.NORMAL, bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1
            )
        else:
            self.name_entry.config(
                state="readonly", bg=BG_COLOR, fg=TEXT_COLOR, relief=tk.FLAT, borderwidth=0
            )

    def _cancel_edit(self) -> None:
        self.name_var.set(self.original_name)
        self._toggle_edit_mode()

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Имя группы не может быть пустым.")
            return

        if self.group_id is not None:
            self._on_save(self.group_id, name)

    def _delete(self) -> None:
        if self.group_id is None:
            return
        confirm = messagebox.askyesno(
            "Удаление",
            f"Вы уверены, что хотите удалить группу '{self.original_name}'?",
        )
        if confirm:
            self._on_delete(self.group_id)
