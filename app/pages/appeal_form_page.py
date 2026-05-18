import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Any
from datetime import datetime

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, show_toast, ICDAutocomplete
)


class AppealFormPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[dict], None], on_cancel: Callable[[], None], 
                 get_person_details_cb: Callable[[str], dict | None],
                 get_next_num_cb: Callable[[], int],
                 search_icd_cb: Callable[[str], list[dict]]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._get_person_details = get_person_details_cb
        self._get_next_num = get_next_num_cb
        self._search_icd = search_icd_cb
        
        self.form_vars: dict[str, tk.StringVar] = {
            "number": tk.StringVar(),
            "created_at": tk.StringVar(),
            "sender": tk.StringVar(),
            "birth_date": tk.StringVar(),
            "group_name": tk.StringVar(),
            "parent_phone": tk.StringVar(),
            "diagnosis": tk.StringVar(),
        }

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=36, pady=(32, 0))
        tk.Label(hdr, text="Оформление обращения", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        
        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 24))

        # Scrollable area if needed, but let's try a compact card first
        card = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 24))
        
        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=24, pady=24)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=1)

        # ── Row 0, 1: Number & Date ────────────────────────────────────────────
        self._add_field(inner, 0, 0, "Номер обращения", "number")
        self._add_field(inner, 0, 1, "Дата обращения", "created_at")

        # ── Row 2, 3: Sender (Combo) ───────────────────────────────────────────
        tk.Label(inner, text="ФИО пациента", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.sender_combo = ctk.CTkComboBox(
            inner, variable=self.form_vars["sender"], state="readonly", font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
            fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
            button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=40,
            command=self._on_sender_selected
        )
        self.sender_combo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # ── Row 4, 5: Birth Date & Group Name (Read-only) ─────────────────────
        self._add_field(inner, 2, 0, "Дата рождения (авто)", "birth_date", readonly=True)
        self._add_field(inner, 2, 1, "Класс/Группа (авто)", "group_name", readonly=True)

        # ── Row 6, 7: Parent Phone ────────────────────────────────────────────
        self._add_field(inner, 3, 0, "Телефон родителей", "parent_phone", columnspan=2)

        # ── Row 8, 9: Complaints ──────────────────────────────────────────────
        tk.Label(inner, text="Жалобы", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=8, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.complaints_text = ctk.CTkTextbox(inner, font=(FONT_FAMILY, 13), fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER, border_width=1, corner_radius=CORNER_RADIUS, height=80)
        self.complaints_text.grid(row=9, column=0, columnspan=2, sticky="ew")

        # ── Row 10, 11: Diagnosis ──────────────────────────────────────────────
        diag_entry = self._add_field(inner, 5, 0, "Предварительный диагноз", "diagnosis", columnspan=2)
        self.diagnosis_autocomplete = ICDAutocomplete(diag_entry, self.form_vars["diagnosis"], self._search_icd)

        # ── Row 12, 13: Recommendations ─────────────────────────────────────────
        tk.Label(inner, text="Оказанная помощь, рекомендации", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=12, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.recommendations_text = ctk.CTkTextbox(inner, font=(FONT_FAMILY, 13), fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER, border_width=1, corner_radius=CORNER_RADIUS, height=80)
        self.recommendations_text.grid(row=13, column=0, columnspan=2, sticky="ew")

        # Actions
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=36, pady=(0, 32))
        
        FlatButton(actions, primary=True, text="Сохранить", command=self._submit, height=44, width=160).pack(side=tk.RIGHT)
        FlatButton(actions, primary=False, text="Отмена", command=self._on_cancel, height=44, width=120).pack(side=tk.RIGHT, padx=(0, 12))

    def _add_field(self, parent, row, col, label, var_key, readonly=False, columnspan=1):
        tk.Label(parent, text=label, font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=row*2, column=col, columnspan=columnspan, sticky="ew", pady=(16, 4), padx=(0 if col==0 else 10, 0))
        entry = ctk.CTkEntry(
            parent, textvariable=self.form_vars[var_key],
            font=(FONT_FAMILY, 14),
            fg_color="#F3F4F6" if readonly else ENTRY_BG, 
            text_color=TEXT_MUTED if readonly else ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
            state="readonly" if readonly else "normal"
        )
        entry.grid(row=row*2+1, column=col, columnspan=columnspan, sticky="ew", pady=(0, 8), padx=(0 if col==0 else 10, 0))
        return entry

    def set_senders(self, senders: list[str]) -> None:
        self.sender_combo.configure(values=senders)

    def reset_form(self) -> None:
        for v in self.form_vars.values():
            v.set("")
        self.complaints_text.delete("1.0", tk.END)
        self.recommendations_text.delete("1.0", tk.END)
        
        # Set defaults
        self.form_vars["number"].set(str(self._get_next_num()))
        self.form_vars["created_at"].set(datetime.now().strftime("%d.%m.%Y"))

    def _on_sender_selected(self, name: str) -> None:
        details = self._get_person_details(name)
        if details:
            self.form_vars["birth_date"].set(details.get("birth_date", ""))
            self.form_vars["group_name"].set(details.get("group_name", ""))
        else:
            self.form_vars["birth_date"].set("")
            self.form_vars["group_name"].set("")

    def _submit(self) -> None:
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        data["complaints"] = self.complaints_text.get("1.0", tk.END).strip()
        data["actions_recommendations"] = self.recommendations_text.get("1.0", tk.END).strip()
        
        errors = []
        if not data["number"]: errors.append("Введите номер обращения.")
        if not data["sender"]: errors.append("Выберите пациента.")
        if not data["created_at"]: errors.append("Укажите дату.")
        
        if errors:
            messagebox.showwarning("Ошибка", "\n".join(errors))
            return
            
        self._on_save(data)
