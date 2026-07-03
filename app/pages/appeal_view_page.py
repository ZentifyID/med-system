import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Any

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, show_toast, ICDAutocomplete
)
from app.date_mask import DateMaskHandler
from app.validators import allow_typed_value, validate_date


class AppealViewPage(tk.Frame):
    def __init__(self, master, on_save: Callable[[int, dict], None], on_delete: Callable[[int], None], 
                 on_cancel: Callable[[], None], search_icd_cb: Callable[[str], list[dict]]) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_delete = on_delete
        self._on_cancel = on_cancel
        self._search_icd = search_icd_cb
        self.person_map = {}
        
        self.appeal_id: int | None = None
        self.original_data: dict | None = None
        self.is_edit_mode = False
        self.senders: list[str] = []

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
        self.page_title = tk.Label(hdr, text="Обращение", font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
        self.page_title.pack(side=tk.LEFT)
        
        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 24))

        # Card Container
        card = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=12
        )
        card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 16))
        
        self.inner = tk.Frame(card, bg=BG_CARD)
        self.inner.pack(fill=tk.X, padx=24, pady=24)
        self.inner.grid_columnconfigure(0, weight=1)
        self.inner.grid_columnconfigure(1, weight=1)

        self.form_entries: dict[str, ctk.CTkEntry] = {}
        self.form_labels: dict[str, tk.Label] = {}

        # ── Row 0: Number & Date ────────────────────────────────────────────────
        self._add_field(self.inner, 0, 0, "Номер обращения", "number")
        self._add_field(self.inner, 0, 1, "Дата обращения", "created_at")

        # ── Row 1: Sender (Combo) ───────────────────────────────────────────────
        tk.Label(self.inner, text="ФИО пациента", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        
        self.sender_label = tk.Label(self.inner, textvariable=self.form_vars["sender"], font=(FONT_FAMILY, 15, "bold"), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
        self.sender_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.sender_combo = ctk.CTkComboBox(
            self.inner, variable=self.form_vars["sender"], state="readonly", font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
            fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
            button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=40,
            command=self._on_sender_selected
        )
        self.sender_combo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.sender_combo.grid_remove()

        # ── Row 4, 5: Birth Date & Group Name (Read-only) ─────────────────────
        self._add_field(self.inner, 2, 0, "Дата рождения (авто)", "birth_date", readonly_always=True)
        self._add_field(self.inner, 2, 1, "Класс/Группа (авто)", "group_name", readonly_always=True)

        # ── Row 6, 7: Parent Phone ────────────────────────────────────────────
        self._add_field(self.inner, 3, 0, "Телефон родителей", "parent_phone", columnspan=2)

        # ── Row 8, 9: Complaints ──────────────────────────────────────────────
        tk.Label(self.inner, text="Жалобы", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=8, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.complaints_text = ctk.CTkTextbox(self.inner, font=(FONT_FAMILY, 13), fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER, border_width=1, corner_radius=CORNER_RADIUS, height=100, undo=True)
        self.complaints_text.grid(row=9, column=0, columnspan=2, sticky="ew")
        self.complaints_text.configure(state="disabled")

        # ── Row 10, 11: Diagnosis ─────────────────────────────────────────────
        self._add_field(self.inner, 5, 0, "Предварительный диагноз", "diagnosis", columnspan=2)
        self.diagnosis_autocomplete = ICDAutocomplete(self.form_entries["diagnosis"], self.form_vars["diagnosis"], self._search_icd)

        # ── Row 12, 13: Recommendations ────────────────────────────────────────
        tk.Label(self.inner, text="Оказанная помощь, рекомендации", font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=12, column=0, columnspan=2, sticky="ew", pady=(16, 4))
        self.recommendations_text = ctk.CTkTextbox(self.inner, font=(FONT_FAMILY, 13), fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER, border_width=1, corner_radius=CORNER_RADIUS, height=100, undo=True)
        self.recommendations_text.grid(row=13, column=0, columnspan=2, sticky="ew")
        self.recommendations_text.configure(state="disabled")

        # Actions
        self.actions = tk.Frame(self, bg=BG_COLOR)
        self.actions.pack(fill=tk.X, padx=36, pady=(0, 32))

        self.edit_button   = FlatButton(self.actions, primary=True,  text="Изменить",  command=self._toggle_edit_mode, height=44, width=140)
        self.delete_button = FlatButton(self.actions, primary=False, danger=True, text="Удалить",   command=self._delete, height=44, width=120)
        self.back_button   = FlatButton(self.actions, primary=False, text="Назад",     command=self._on_cancel, height=44, width=100)
        self.save_button   = FlatButton(self.actions, primary=True,  text="Сохранить", command=self._submit, height=44, width=160)
        self.cancel_button = FlatButton(self.actions, primary=False, text="Отмена",    command=self._cancel_edit, height=44, width=120)

        self._show_view_actions()

    def _add_field(self, parent, row, col, label, var_key, readonly_always=False, columnspan=1):
        tk.Label(parent, text=label, font=(FONT_MEDIUM, 11), bg=BG_CARD, fg=TEXT_MUTED, anchor="w").grid(row=row*2, column=col, columnspan=columnspan, sticky="ew", pady=(16, 4), padx=(0 if col==0 else 10, 0))
        
        # View mode label
        lbl = tk.Label(parent, textvariable=self.form_vars[var_key], font=(FONT_FAMILY, 13), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
        lbl.grid(row=row*2+1, column=col, columnspan=columnspan, sticky="ew", pady=(0, 8), padx=(0 if col==0 else 10, 0))
        self.form_labels[var_key] = lbl
        
        vcmd = None
        if var_key == "created_at":
            vcmd = (self.register(lambda p: allow_typed_value("created_at", p)), "%P")
        elif var_key == "number":
            vcmd = (self.register(lambda p: p.isdigit() or p == ""), "%P")

        # Edit mode entry
        entry = ctk.CTkEntry(
            parent, textvariable=self.form_vars[var_key],
            font=(FONT_FAMILY, 14),
            fg_color="#F4F4F5" if readonly_always else ENTRY_BG, 
            text_color=TEXT_MUTED if readonly_always else ENTRY_FG,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=40,
            state="readonly" if readonly_always else "normal",
            validate="key" if vcmd else "none",
            validatecommand=vcmd
        )
        entry.grid(row=row*2+1, column=col, columnspan=columnspan, sticky="ew", pady=(0, 8), padx=(0 if col==0 else 10, 0))
        entry.grid_remove()
        self.form_entries[var_key] = entry
        
        if var_key == "created_at":
            DateMaskHandler.bind_to_entry(entry, self.form_vars[var_key])

    def _show_view_actions(self):
        self.edit_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT, padx=(12, 0))
        self.back_button.pack(side=tk.RIGHT)

    def set_senders(self, persons: list[dict]) -> None:
        self.person_map = {p["display"]: p for p in persons}
        self.senders = list(self.person_map.keys())
        self.sender_combo.configure(values=self.senders)

    def set_appeal_data(self, data: dict) -> None:
        self.appeal_id = int(data["id"])
        self.original_data = data.copy()
        self.page_title.config(text=f"Обращение №{data.get('number', '')}")
        
        for k, v in self.form_vars.items():
            v.set(data.get(k, ""))
            
        self.complaints_text.configure(state="normal")
        self.complaints_text.delete("1.0", tk.END)
        self.complaints_text.insert(tk.END, data.get("complaints", ""))
        self._reset_text_undo(self.complaints_text)
        self.complaints_text.configure(state="disabled")

        self.recommendations_text.configure(state="normal")
        self.recommendations_text.delete("1.0", tk.END)
        self.recommendations_text.insert(tk.END, data.get("actions_recommendations", ""))
        self._reset_text_undo(self.recommendations_text)
        self.recommendations_text.configure(state="disabled")
        
        if self.is_edit_mode: self._toggle_edit_mode()

    def _toggle_edit_mode(self) -> None:
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.edit_button.pack_forget(); self.delete_button.pack_forget(); self.back_button.pack_forget()
            self.save_button.pack(side=tk.RIGHT); self.cancel_button.pack(side=tk.RIGHT, padx=(0, 12))
            
            # Switch labels to entries
            for k, lbl in self.form_labels.items():
                lbl.grid_remove()
                self.form_entries[k].grid()
            
            self.sender_label.grid_remove()
            self.sender_combo.grid()
            
            self.complaints_text.configure(state="normal")
            self.recommendations_text.configure(state="normal")
        else:
            self.save_button.pack_forget(); self.cancel_button.pack_forget()
            self._show_view_actions()
            
            # Switch entries to labels
            for k, entry in self.form_entries.items():
                entry.grid_remove()
                self.form_labels[k].grid()
            
            self.sender_combo.grid_remove()
            self.sender_label.grid()
            
            self.complaints_text.configure(state="disabled")
            self.recommendations_text.configure(state="disabled")

    def _on_sender_selected(self, name: str) -> None:
        details = self.person_map.get(name)
        if details:
            self.form_vars["birth_date"].set(details.get("birth_date", ""))
            self.form_vars["group_name"].set(details.get("group_name", ""))

    def _reset_text_undo(self, textbox: ctk.CTkTextbox) -> None:
        inner_text = textbox._textbox if hasattr(textbox, "_textbox") else textbox
        try:
            inner_text.edit_reset()
        except tk.TclError:
            pass

    def _cancel_edit(self) -> None:
        if self.original_data:
            self.set_appeal_data(self.original_data)

    def _delete(self) -> None:
        if self.appeal_id and messagebox.askyesno("Подтверждение", "Удалить это обращение?"):
            self._on_delete(self.appeal_id)

    def _submit(self) -> None:
        if not self.appeal_id: return
        data = {k: v.get().strip() for k, v in self.form_vars.items()}
        data["complaints"] = self.complaints_text.get("1.0", tk.END).strip()
        data["actions_recommendations"] = self.recommendations_text.get("1.0", tk.END).strip()
        
        errors = []
        if not data["number"]: errors.append("Введите номер обращения.")
        if not data["sender"]: errors.append("Выберите пациента.")
        if not data["created_at"] or data["created_at"] == "__.__.____":
            errors.append("Укажите дату.")
        elif not validate_date(data["created_at"]):
            errors.append("Неверный формат даты обращения (ожидается ДД.ММ.ГГГГ).")
            
        if errors:
            messagebox.showwarning("Ошибка", "\n".join(errors))
            return
            
        self._on_save(self.appeal_id, data)
