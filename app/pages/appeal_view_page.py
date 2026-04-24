import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from app.ui import BG_COLOR, TEXT_COLOR, ENTRY_BG, ENTRY_FG, FlatButton


class AppealViewPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[int, dict[str, str]], None],
        on_delete: Callable[[int], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel

        self.title_var = tk.StringVar()
        self.sender_var = tk.StringVar()
        self.created_at_var = tk.StringVar()
        
        self.original_data: dict[str, str] | None = None
        self.appeal_id: int | None = None
        self.is_edit_mode = False
        self.senders: list[str] = []

        self.page_title = tk.Label(
            self,
            text="Просмотр обращения",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self.page_title.pack(pady=(20, 12))

        self.form_container = tk.Frame(self, bg=BG_COLOR)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Title
        tk.Label(
            self.form_container,
            text="Заголовок",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.title_label = tk.Label(self.form_container, textvariable=self.title_var, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR, anchor="w")
        self.title_label.pack(fill=tk.X, pady=(0, 15))
        self.title_entry = tk.Entry(self.form_container, textvariable=self.title_var, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)

        # Sender & Created At (side by side in view mode)
        self.info_frame = tk.Frame(self.form_container, bg=BG_COLOR)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(self.info_frame, text="От кого:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        self.sender_label = tk.Label(self.info_frame, textvariable=self.sender_var, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR)
        self.sender_label.pack(side=tk.LEFT, padx=(5, 20))
        
        tk.Label(self.info_frame, text="Дата создания:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        tk.Label(self.info_frame, textvariable=self.created_at_var, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(5, 0))

        # Sender edit mode
        self.sender_edit_frame = tk.Frame(self.form_container, bg=BG_COLOR)
        tk.Label(self.sender_edit_frame, text="От кого", font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 5))
        self.sender_combo = ttk.Combobox(self.sender_edit_frame, textvariable=self.sender_var, state="readonly", font=("Segoe UI", 10))
        self.sender_combo.pack(fill=tk.X, pady=(0, 15))

        # Text
        tk.Label(
            self.form_container,
            text="Текст обращения",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.text_widget = tk.Text(
            self.form_container,
            font=("Segoe UI", 10),
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief=tk.SOLID,
            borderwidth=1,
            height=10,
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        # Initial state is disabled
        self.text_widget.config(state=tk.DISABLED)

        # Actions
        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=30, pady=(10, 30))

        self.edit_button = FlatButton(self.actions, primary=True, text="Изменить", width=14, command=self._toggle_edit_mode)
        self.edit_button.pack(side=tk.LEFT)

        self.delete_button = FlatButton(self.actions, primary=False, text="Удалить", width=14, command=self._delete_action)
        self.delete_button.pack(side=tk.LEFT, padx=(12, 0))

        self.back_button = FlatButton(self.actions, primary=False, text="Назад", width=14, command=self._on_cancel)
        self.back_button.pack(side=tk.LEFT, padx=(12, 0))

        self.save_button = FlatButton(self.actions, primary=True, text="Сохранить", width=14, command=self._submit)
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена", width=14, command=self._cancel_edit)

    def set_senders(self, senders: list[str]) -> None:
        self.senders = senders
        self.sender_combo["values"] = senders

    def set_appeal_data(self, data: dict[str, str]) -> None:
        self.appeal_id = int(data["id"])
        self.original_data = data.copy()
        
        self.page_title.config(text=f"Обращение: {data.get('title', '')}")
        self.title_var.set(data.get("title", ""))
        self.sender_var.set(data.get("sender", ""))
        self.created_at_var.set(data.get("created_at", ""))
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, data.get("text", ""))
        self.text_widget.config(state=tk.DISABLED)
        
        if self.is_edit_mode:
            self._toggle_edit_mode()

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.pack_forget()
            self.delete_button.pack_forget()
            self.back_button.pack_forget()
            self.save_button.pack(side=tk.LEFT)
            self.cancel_button.pack(side=tk.LEFT, padx=(10, 0))

            self.title_label.pack_forget()
            self.title_entry.pack(fill=tk.X, pady=(0, 15), before=self.info_frame)
            
            self.info_frame.pack_forget()
            self.sender_edit_frame.pack(fill=tk.X, pady=(0, 15), before=self.text_widget)
            
            self.text_widget.config(state=tk.NORMAL)
            
            # Ensure the current sender is in the list, if it was deleted or changed
            if self.sender_var.get() not in self.senders:
                self.sender_combo["values"] = self.senders + [self.sender_var.get()]
        else:
            self.save_button.pack_forget()
            self.cancel_button.pack_forget()
            self.edit_button.pack(side=tk.LEFT)
            self.delete_button.pack(side=tk.LEFT, padx=(10, 0))
            self.back_button.pack(side=tk.LEFT, padx=(10, 0))

            self.title_entry.pack_forget()
            self.title_label.pack(fill=tk.X, pady=(0, 15), before=self.sender_edit_frame)
            
            self.sender_edit_frame.pack_forget()
            self.info_frame.pack(fill=tk.X, pady=(0, 15), before=self.text_widget)
            
            self.text_widget.config(state=tk.DISABLED)

    def _cancel_edit(self) -> None:
        if self.original_data:
            self.title_var.set(self.original_data.get("title", ""))
            self.sender_var.set(self.original_data.get("sender", ""))
            
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, self.original_data.get("text", ""))
            self.text_widget.config(state=tk.DISABLED)
            
        self._toggle_edit_mode()

    def _delete_action(self) -> None:
        if self.appeal_id is not None:
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это обращение?"):
                self._on_delete(self.appeal_id)

    def _submit(self) -> None:
        if self.appeal_id is None:
            return
            
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

        self._on_save(self.appeal_id, data)
