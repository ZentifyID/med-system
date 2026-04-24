import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Any

from app.ui import BG_COLOR, TEXT_COLOR, FlatButton, ENTRY_BG, ENTRY_FG


class OrderMedicinesDialog(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        medicines_to_order: list[dict[str, Any]],
        on_confirm: Callable[[list[dict[str, Any]]], None],
    ):
        super().__init__(master)
        self.title("Оформление заказа лекарств")
        self.geometry("700x550")
        self.configure(bg=BG_COLOR)
        self.transient(master)  # type: ignore
        self.grab_set()
        
        self.on_confirm = on_confirm
        self.medicines_to_order = medicines_to_order
        
        self.item_vars: dict[int, dict[str, Any]] = {}
        
        lbl = tk.Label(
            self, 
            text="Выберите лекарства для заказа и укажите новые данные:", 
            bg=BG_COLOR, 
            fg=TEXT_COLOR,
            font=("Segoe UI", 12, "bold")
        )
        lbl.pack(pady=(20, 10), padx=20, anchor=tk.W)

        # Scrollable area
        frame_container = tk.Frame(self, bg=BG_COLOR)
        frame_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(frame_container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=640)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate list
        for idx, med in enumerate(self.medicines_to_order):
            m_id = med["id"]
            name = med["name"]
            unit = med["unit"]
            qty = med["quantity"]
            exp = med["expiration_date"]
            
            row_frame = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
            row_frame.pack(fill=tk.X, pady=5)
            
            check_var = tk.BooleanVar(value=True)
            qty_var = tk.StringVar()
            exp_var = tk.StringVar(value="")
            
            self.item_vars[m_id] = {
                "check": check_var,
                "qty": qty_var,
                "exp": exp_var,
                "name": name,
                "unit": unit
            }
            
            chk = tk.Checkbutton(
                row_frame, 
                text=f"{name} (Остаток: {qty} {unit}, Годен до: {exp})", 
                variable=check_var,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 10),
                selectcolor=BG_COLOR,
                activebackground=BG_COLOR,
            )
            chk.pack(anchor=tk.W)
            
            inputs_frame = tk.Frame(row_frame, bg=BG_COLOR)
            inputs_frame.pack(fill=tk.X, padx=(25, 0), pady=(5, 0))
            
            tk.Label(inputs_frame, text="Новое кол-во:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            qty_entry = tk.Entry(inputs_frame, textvariable=qty_var, width=10, bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
            qty_entry.pack(side=tk.LEFT, padx=(5, 15))
            
            tk.Label(inputs_frame, text="Новый срок (ДД.ММ.ГГГГ):", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            exp_entry = tk.Entry(inputs_frame, textvariable=exp_var, width=12, bg=ENTRY_BG, fg=ENTRY_FG, relief=tk.SOLID, borderwidth=1)
            exp_entry.pack(side=tk.LEFT, padx=(5, 0))
            
            tk.Frame(self.scrollable_frame, height=1, bg="#e0e0e0").pack(fill=tk.X, pady=5)

        # Buttons
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=20, pady=20)

        confirm_button = FlatButton(
            actions,
            primary=True,
            text="Подтвердить заказ",
            width=18,
            command=self._on_confirm_click,
        )
        confirm_button.pack(side=tk.LEFT)

        cancel_button = FlatButton(
            actions,
            primary=False,
            text="Отмена",
            width=14,
            command=self.destroy,
        )
        cancel_button.pack(side=tk.LEFT, padx=(12, 0))

    def _on_confirm_click(self) -> None:
        result_to_order = []
        errors = []
        
        for m_id, vars_dict in self.item_vars.items():
            if not vars_dict["check"].get():
                continue
                
            qty_str = vars_dict["qty"].get().strip()
            exp_str = vars_dict["exp"].get().strip()
            name = vars_dict["name"]
            
            if not qty_str:
                errors.append(f"Укажите количество для: {name}")
            elif not qty_str.isdigit():
                errors.append(f"Количество должно быть числом для: {name}")
                
            if not exp_str or len(exp_str) != 10 or exp_str.count(".") != 2:
                errors.append(f"Некорректный срок годности (ДД.ММ.ГГГГ) для: {name}")
                
            if not errors:
                result_to_order.append({
                    "old_id": m_id,
                    "name": name,
                    "unit": vars_dict["unit"],
                    "new_quantity": qty_str,
                    "new_expiration_date": exp_str,
                })

        if errors:
            messagebox.showwarning("Ошибка заполнения", "\n".join(errors[:10]), parent=self)
            return
            
        if not result_to_order:
            messagebox.showinfo("Информация", "Вы не выбрали ни одного лекарства для заказа.", parent=self)
            return
            
        if messagebox.askyesno("Подтверждение", "Выбранные старые партии будут списаны (удалены), а новые добавлены. Продолжить?", parent=self):
            self.on_confirm(result_to_order)
            self.destroy()
