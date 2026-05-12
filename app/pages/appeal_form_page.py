import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, show_toast
)


class AppealFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self.title_var = tk.StringVar()
        self.sender_var = tk.StringVar()
        self.draft_data = {"title": "", "sender": "", "text": ""}

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
        self.title_entry = ctk.CTkEntry(
            inner, textvariable=self.title_var,
            font=(FONT_FAMILY, 14),
            fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
        )
        self.title_entry.pack(fill=tk.X, pady=(0, 16))
        
        # Inline validation reset on focus in
        self.title_entry.bind("<FocusIn>", lambda e: self.title_entry.configure(border_color=ENTRY_BORDER))

        # Sender
        tk.Label(inner, text="От кого", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.sender_combo = ctk.CTkComboBox(
            inner, variable=self.sender_var, state="readonly", font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
            fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
            button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=40
        )
        self.sender_combo.pack(fill=tk.X, pady=(0, 16))

        # Text
        tk.Label(inner, text="Текст обращения", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.text_widget = ctk.CTkTextbox(
            inner, 
            font=(FONT_FAMILY, 14), 
            fg_color=ENTRY_BG, 
            text_color=ENTRY_FG,
            border_color=ENTRY_BORDER,
            border_width=1,
            corner_radius=CORNER_RADIUS,
            height=160,
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Actions
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=36, pady=(0, 32))
        
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, height=44, width=160).pack(side=tk.RIGHT)
        FlatButton(actions, primary=False, text="Отмена", command=self._cancel_and_save_draft, height=44, width=120).pack(side=tk.RIGHT, padx=(0, 12))

    def set_senders(self, senders: list[str]) -> None:
        self.sender_combo.configure(values=senders)

    def reset_form(self) -> None:
        self.title_var.set(self.draft_data["title"])
        self.sender_var.set(self.draft_data["sender"])
        self.text_widget.delete("1.0", tk.END)
        if self.draft_data["text"]:
            self.text_widget.insert("1.0", self.draft_data["text"])
            
        self.title_entry.configure(border_color=ENTRY_BORDER)
        self.text_widget.configure(border_color=ENTRY_BORDER)

    def _cancel_and_save_draft(self) -> None:
        self.draft_data["title"] = self.title_var.get()
        self.draft_data["sender"] = self.sender_var.get()
        self.draft_data["text"] = self.text_widget.get("1.0", tk.END).strip()
        
        self.title_entry.configure(border_color=ENTRY_BORDER)
        self.text_widget.configure(border_color=ENTRY_BORDER)
        self._on_cancel()

    def _submit(self) -> None:
        data = {"title": self.title_var.get().strip(), "sender": self.sender_var.get().strip(), "text": self.text_widget.get("1.0", tk.END).strip()}
        errors = []
        
        if not data["title"]: 
            errors.append("Введите заголовок.")
            self.title_entry.configure(border_color="#EF4444")
        if not data["sender"]: 
            errors.append("Выберите отправителя.")
        if not data["text"]: 
            errors.append("Введите текст обращения.")
            self.text_widget.configure(border_color="#EF4444")
            
        if errors:
            show_toast(self.winfo_toplevel(), "\n".join(errors), "error")
            return
            
        # Clear draft after successful submit
        self.draft_data = {"title": "", "sender": "", "text": ""}
        self._on_save(data)
