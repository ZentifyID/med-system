import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Any

import customtkinter as ctk

from app.ui import BG_CARD, BG_COLOR, TEXT_COLOR, TEXT_MUTED, BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, ACCENT, CORNER_RADIUS, FlatButton


class OrderMedicinesDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, medicines_to_order: list[dict[str, Any]], on_confirm: Callable[[list[dict[str, Any]]], None]):
        super().__init__(master)
        self.title("Оформление заказа лекарств")
        self.geometry("740x580")
        self.configure(bg=BG_COLOR)
        self.transient(master)  # type: ignore
        self.grab_set()
        self.on_confirm = on_confirm
        self.medicines_to_order = medicines_to_order
        self.item_vars: dict[int, dict[str, Any]] = {}

        # Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=24, pady=(20, 0))
        tk.Label(hdr, text="Заказ лекарств", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=24, pady=(10, 14))
        tk.Label(self, text="Выберите позиции и укажите новые данные:", font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_MUTED).pack(anchor="w", padx=24, pady=(0, 10))

        # Scrollable area
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill=tk.BOTH, expand=True, padx=24)
        canvas = tk.Canvas(outer, bg=BG_COLOR, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=670)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        for med in self.medicines_to_order:
            m_id = med["id"]
            check_var = tk.BooleanVar(value=True)
            qty_var = tk.StringVar()
            exp_var = tk.StringVar()
            self.item_vars[m_id] = {"check": check_var, "qty": qty_var, "exp": exp_var, "name": med["name"], "unit": med["unit"]}

            row = tk.Frame(self.scroll_frame, bg=BG_CARD)
            row.pack(fill=tk.X, pady=4)
            tk.Frame(row, bg=ACCENT, width=4).pack(side=tk.LEFT, fill=tk.Y)
            content = tk.Frame(row, bg=BG_CARD)
            content.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=10)

            top = tk.Frame(content, bg=BG_CARD)
            top.pack(fill=tk.X)
            tk.Checkbutton(top, variable=check_var, bg=BG_CARD, activebackground=BG_CARD, selectcolor=BG_CARD).pack(side=tk.LEFT)
            tk.Label(top, text=f"{med['name']}", font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(top, text=f"  Остаток: {med['quantity']} {med['unit']}  |  Годен до: {med['expiration_date']}", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)

            inputs = tk.Frame(content, bg=BG_CARD)
            inputs.pack(fill=tk.X, pady=(6, 0))
            tk.Label(inputs, text="Новое кол-во:", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
            ctk.CTkEntry(
                inputs, textvariable=qty_var, width=80,
                fg_color=ENTRY_BG, text_color=ENTRY_FG,
                border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=30,
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).pack(side=tk.LEFT, padx=(4, 16))
            tk.Label(inputs, text="Срок (ДД.ММ.ГГГГ):", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
            ctk.CTkEntry(
                inputs, textvariable=exp_var, width=120,
                fg_color=ENTRY_BG, text_color=ENTRY_FG,
                border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS, height=30,
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).pack(side=tk.LEFT, padx=(4, 0))

        # Actions
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=24, pady=(12, 0))
        bar = tk.Frame(self, bg=BG_COLOR)
        bar.pack(fill=tk.X, padx=24, pady=16)
        FlatButton(bar, primary=True, text="Подтвердить заказ", command=self._on_confirm_click, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side=tk.LEFT)
        FlatButton(bar, primary=False, text="Отмена", command=self.destroy, font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side=tk.LEFT, padx=(10, 0))

    def _on_confirm_click(self) -> None:
        result = []
        errors = []
        for m_id, v in self.item_vars.items():
            if not v["check"].get(): continue
            qty_str = v["qty"].get().strip()
            exp_str = v["exp"].get().strip()
            name = v["name"]
            if not qty_str: errors.append(f"Укажите количество для: {name}")
            elif not qty_str.isdigit(): errors.append(f"Количество должно быть числом: {name}")
            if not exp_str or len(exp_str) != 10 or exp_str.count(".") != 2:
                errors.append(f"Некорректный срок годности: {name}")
            if not errors:
                result.append({"old_id": m_id, "name": name, "unit": v["unit"], "new_quantity": qty_str, "new_expiration_date": exp_str})
        if errors: messagebox.showwarning("Ошибка", "\n".join(errors[:10]), parent=self); return
        if not result: messagebox.showinfo("Информация", "Не выбрано ни одной позиции.", parent=self); return
        if messagebox.askyesno("Подтверждение", "Старые партии будут списаны. Продолжить?", parent=self):
            self.on_confirm(result)
            self.destroy()
