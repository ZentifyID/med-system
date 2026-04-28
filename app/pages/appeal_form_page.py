import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, 
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM
)


class AppealFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self.title_var = tk.StringVar()
        self.sender_var = tk.StringVar()

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        tk.Label(hdr, text="Создание обращения", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        
        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 24))

        # Card Container
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 24))
        
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Title
        tk.Label(inner, text="Заголовок", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        ctk.CTkEntry(
            inner, textvariable=self.title_var,
            font=(FONT_FAMILY, 14),
            fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
        ).pack(fill=tk.X, pady=(0, 16))

        # Sender
        tk.Label(inner, text="От кого", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.sender_combo = ttk.Combobox(inner, textvariable=self.sender_var, state="readonly", font=(FONT_FAMILY, 10))
        self.sender_combo.pack(fill=tk.X, pady=(0, 16))

        # Text
        tk.Label(inner, text="Текст обращения", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        # Container for text widget to have border
        text_frame = tk.Frame(inner, bg=ENTRY_BORDER, padx=1, pady=1)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame, 
            font=(FONT_FAMILY, 11), 
            bg=ENTRY_BG, 
            fg=ENTRY_FG, 
            relief=tk.FLAT, 
            padx=10, 
            pady=10,
            height=8
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Actions
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=36, pady=(0, 32))
        
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, height=44, width=160).pack(side=tk.RIGHT)
        FlatButton(actions, primary=False, text="Отмена", command=self._on_cancel, height=44, width=120).pack(side=tk.RIGHT, padx=(0, 12))

    def set_senders(self, senders: list[str]) -> None:
        self.sender_combo["values"] = senders

    def reset_form(self) -> None:
        self.title_var.set("")
        self.sender_var.set("")
        self.text_widget.delete("1.0", tk.END)

    def _submit(self) -> None:
        data = {"title": self.title_var.get().strip(), "sender": self.sender_var.get().strip(), "text": self.text_widget.get("1.0", tk.END).strip()}
        errors = []
        if not data["title"]: errors.append("Введите заголовок.")
        if not data["sender"]: errors.append("Выберите отправителя.")
        if not data["text"]: errors.append("Введите текст обращения.")
        if errors: messagebox.showwarning("Ошибка", "\n".join(errors)); return
        self._on_save(data)


class AppealViewPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[int, dict], None], on_delete: Callable[[int], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self.title_var = tk.StringVar()
        self.sender_var = tk.StringVar()
        self.created_at_var = tk.StringVar()
        self.original_data: dict | None = None
        self.appeal_id: int | None = None
        self.is_edit_mode = False
        self.senders: list[str] = []

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        self.page_title = tk.Label(hdr, text="Обращение", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.page_title.pack(side=tk.LEFT)
        
        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 24))

        # Card Container
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 16))
        
        self.form_container = tk.Frame(card, bg=BG_CARD)
        self.form_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Heading label
        tk.Label(self.form_container, text="Заголовок", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.title_label = tk.Label(self.form_container, textvariable=self.title_var, font=(FONT_FAMILY, 18, "bold"), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
        self.title_label.pack(fill=tk.X, pady=(0, 16))
        
        self.title_entry = ctk.CTkEntry(
            self.form_container, textvariable=self.title_var,
            font=(FONT_FAMILY, 14),
            fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
        )

        # Info row (view mode)
        self.info_frame = tk.Frame(self.form_container, bg=BG_CARD)
        self.info_frame.pack(fill=tk.X, pady=(0, 16))
        tk.Label(self.info_frame, text="От кого:", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
        self.sender_label = tk.Label(self.info_frame, textvariable=self.sender_var, font=(FONT_FAMILY, 11), bg=BG_CARD, fg=TEXT_COLOR)
        self.sender_label.pack(side=tk.LEFT, padx=(6, 20))
        tk.Label(self.info_frame, text="Дата:", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
        tk.Label(self.info_frame, textvariable=self.created_at_var, font=(FONT_FAMILY, 11), bg=BG_CARD, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(6, 0))

        # Sender edit mode
        self.sender_edit_frame = tk.Frame(self.form_container, bg=BG_CARD)
        tk.Label(self.sender_edit_frame, text="От кого", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.sender_combo = ttk.Combobox(self.sender_edit_frame, textvariable=self.sender_var, state="readonly", font=(FONT_FAMILY, 10))
        self.sender_combo.pack(fill=tk.X, pady=(0, 16))

        # Text
        tk.Label(self.form_container, text="Текст обращения", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.text_box_frame = tk.Frame(self.form_container, bg=ENTRY_BORDER, padx=1, pady=1)
        self.text_box_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            self.text_box_frame, 
            font=(FONT_FAMILY, 11), 
            bg=ENTRY_BG, 
            fg=ENTRY_FG, 
            relief=tk.FLAT, 
            padx=10, 
            pady=10, 
            height=10, 
            state=tk.DISABLED
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Actions
        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=36, pady=(0, 32))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, height=44, width=140)
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить",   command=self._delete, height=44, width=120)
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, height=44, width=100)
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, height=44, width=160)
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, height=44, width=120)

        self._show_view_actions()

    def _show_view_actions(self):
        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(12, 0))
        self.back_button.pack(side=tk.RIGHT)

    def set_senders(self, senders: list[str]) -> None:
        self.senders = senders
        self.sender_combo["values"] = senders

    def set_appeal_data(self, data: dict) -> None:
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
        if self.is_edit_mode: self._toggle_edit_mode()

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.pack_forget(); self.delete_button.pack_forget(); self.back_button.pack_forget()
            self.save_button.pack(side=tk.RIGHT); self.cancel_button.pack(side=tk.RIGHT, padx=(0, 12))
            self.title_label.pack_forget()
            self.title_entry.pack(fill=tk.X, pady=(0, 16), before=self.info_frame)
            self.info_frame.pack_forget()
            self.sender_edit_frame.pack(fill=tk.X, pady=(0, 16), before=self.text_box_frame)
            self.text_widget.config(state=tk.NORMAL)
            if self.sender_var.get() not in self.senders:
                self.sender_combo["values"] = self.senders + [self.sender_var.get()]
        else:
            self.save_button.pack_forget(); self.cancel_button.pack_forget()
            self._show_view_actions()
            self.title_entry.pack_forget()
            self.title_label.pack(fill=tk.X, pady=(0, 16), before=self.sender_edit_frame)
            self.sender_edit_frame.pack_forget()
            self.info_frame.pack(fill=tk.X, pady=(0, 16), before=self.text_box_frame)
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

    def _delete(self) -> None:
        if self.appeal_id and messagebox.askyesno("Подтверждение", "Удалить это обращение?"):
            self._on_delete(self.appeal_id)

    def _submit(self) -> None:
        if not self.appeal_id: return
        data = {"title": self.title_var.get().strip(), "sender": self.sender_var.get().strip(), "text": self.text_widget.get("1.0", tk.END).strip()}
        errors = []
        if not data["title"]: errors.append("Введите заголовок.")
        if not data["sender"]: errors.append("Выберите отправителя.")
        if not data["text"]: errors.append("Введите текст.")
        if errors: messagebox.showwarning("Ошибка", "\n".join(errors)); return
        self._on_save(self.appeal_id, data)
