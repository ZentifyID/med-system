import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from app.ui import (
    BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    CORNER_RADIUS, FlatButton, FONT_FAMILY, FONT_MEDIUM,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER
)


class AddEditICDDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, old_code: str = None, old_name: str = None):
        super().__init__(master)
        self.on_save = on_save
        self.old_code = old_code
        self.old_name = old_name
        self.is_edit = old_code is not None

        self.title("Редактирование МКБ-10" if self.is_edit else "Добавление МКБ-10")
        self.geometry("440x320")
        self.resizable(False, False)
        self.configure(fg_color=BG_CARD)
        self.transient(master)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (440 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (320 // 2)
        self.geometry(f"+{x}+{y}")

        # Title
        label = ctk.CTkLabel(
            self,
            text="Изменение диагноза" if self.is_edit else "Новый код МКБ-10",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=TEXT_COLOR
        )
        label.pack(pady=(24, 16))

        # Variables
        self.code_var = tk.StringVar(value=old_code or "")
        self.name_var = tk.StringVar(value=old_name or "")

        # Code Field
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill=tk.X, padx=36)

        ctk.CTkLabel(form_frame, text="Код МКБ-10:", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(4, 2))
        self.code_entry = ctk.CTkEntry(
            form_frame, textvariable=self.code_var,
            font=(FONT_FAMILY, 14), fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=38
        )
        self.code_entry.pack(fill=tk.X, pady=(0, 10))

        # Name Field
        ctk.CTkLabel(form_frame, text="Наименование диагноза:", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_MUTED, anchor="w").pack(fill=tk.X, pady=(4, 2))
        self.name_entry = ctk.CTkEntry(
            form_frame, textvariable=self.name_var,
            font=(FONT_FAMILY, 14), fg_color=ENTRY_BG, text_color=ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=38
        )
        self.name_entry.pack(fill=tk.X, pady=(0, 16))

        # Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=36, pady=20)

        FlatButton(
            btn_frame, text="Сохранить" if self.is_edit else "Добавить",
            primary=True, command=self._submit, height=40, width=120
        ).pack(side=tk.RIGHT)

        FlatButton(
            btn_frame, text="Отмена", primary=False,
            command=self.destroy, height=40, width=100
        ).pack(side=tk.RIGHT, padx=12)

    def _submit(self):
        code = self.code_var.get().strip()
        name = self.name_var.get().strip()

        if not code:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите код МКБ-10 (например: J06.9).")
            return
        if not name:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите наименование диагноза.")
            return

        # Trigger callback
        if self.is_edit:
            success = self.on_save(self.old_code, code, name)
        else:
            success = self.on_save(code, name)

        if success:
            self.destroy()
        else:
            messagebox.showerror("Ошибка", f"Код МКБ-10 '{code}' уже существует в справочнике!")
