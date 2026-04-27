import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk

from app.ui import (
    BG_CARD, BG_COLOR, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_FG, ACCENT_LIGHT,
    BORDER, CORNER_RADIUS, FlatButton,
)
from app.database import (
    fetch_employees_for_table,
    fetch_students_for_table,
    fetch_medicines_for_table,
    fetch_appeals_for_table,
)


class MainPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_employees: Callable[[], None],
        on_students: Callable[[], None],
        on_medicines: Callable[[], None],
        on_appeals: Callable[[], None],
        on_add_employee: Callable[[], None] | None = None,
        on_add_student: Callable[[], None] | None = None,
        on_add_medicine: Callable[[], None] | None = None,
        on_add_appeal: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_employees = on_employees
        self._on_students = on_students
        self._on_medicines = on_medicines
        self._on_appeals = on_appeals
        self._on_add_employee = on_add_employee or on_employees
        self._on_add_student = on_add_student or on_students
        self._on_add_medicine = on_add_medicine or on_medicines
        self._on_add_appeal = on_add_appeal or on_appeals

        # Header
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=36, pady=(36, 4))

        tk.Label(
            header,
            text="Главная",
            font=("Segoe UI", 20, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="Обзор системы",
            font=("Segoe UI", 11),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        ).pack(side=tk.LEFT, padx=(16, 0), pady=(4, 0))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(8, 28))

        # Stats cards row
        self.cards_frame = tk.Frame(self, bg=BG_COLOR)
        self.cards_frame.pack(fill=tk.X, padx=36, pady=(0, 32))

        card_defs = [
            ("👤", "Сотрудники", "0", on_employees),
            ("🎓", "Студенты", "0", on_students),
            ("💊", "Лекарства", "0", on_medicines),
            ("📋", "Обращения", "0", on_appeals),
        ]

        for i, (icon, label, count, cmd) in enumerate(card_defs):
            card = self._build_stat_card(self.cards_frame, icon, label, count, cmd)
            card.grid(row=0, column=i, padx=(0, 16) if i < 3 else 0, sticky="nsew")
            self.cards_frame.grid_columnconfigure(i, weight=1)

        # Quick action section
        tk.Label(
            self,
            text="Быстрый доступ",
            font=("Segoe UI", 13, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(anchor="w", padx=36, pady=(0, 14))

        actions_frame = tk.Frame(self, bg=BG_COLOR)
        actions_frame.pack(fill=tk.X, padx=36)

        quick_buttons = [
            ("+ Добавить сотрудника", self._on_add_employee),
            ("+ Добавить студента", self._on_add_student),
            ("+ Добавить лекарство", self._on_add_medicine),
            ("+ Новое обращение", self._on_add_appeal),
        ]

        for i, (text, cmd) in enumerate(quick_buttons):
            btn = FlatButton(
                actions_frame,
                primary=True,
                text=text,
                command=cmd,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                height=40,
            )
            btn.grid(row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="ew")
            actions_frame.grid_columnconfigure(i, weight=1)

    def _build_stat_card(
        self,
        parent: tk.Frame,
        icon: str,
        label: str,
        count: str,
        command: Callable,
    ) -> tk.Frame:
        # Outer card with subtle border
        card = tk.Frame(parent, bg=BORDER, cursor="hand2", bd=0)

        # Inner white content (1px border effect via padding)
        inner_wrap = tk.Frame(card, bg=BG_CARD)
        inner_wrap.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        inner = tk.Frame(inner_wrap, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)

        # Icon + count row
        top_row = tk.Frame(inner, bg=BG_CARD)
        top_row.pack(fill=tk.X)

        icon_lbl = tk.Label(top_row, text=icon, font=("Segoe UI", 20), bg=BG_CARD, fg=TEXT_COLOR)
        icon_lbl.pack(side=tk.LEFT)

        count_lbl = tk.Label(top_row, text=count, font=("Segoe UI", 26, "bold"), bg=BG_CARD, fg=TEXT_COLOR)
        count_lbl.pack(side=tk.RIGHT)

        # Label
        label_lbl = tk.Label(inner, text=label, font=("Segoe UI", 10), bg=BG_CARD, fg=TEXT_MUTED)
        label_lbl.pack(anchor="w", pady=(8, 4))

        # Click link
        open_btn = tk.Label(
            inner,
            text="Открыть →",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=ACCENT,
            cursor="hand2",
        )
        open_btn.pack(anchor="w")

        # Hover
        hover_bg = "#F9FAFB"

        def _set_bg(target_bg):
            inner_wrap.configure(bg=target_bg)
            inner.configure(bg=target_bg)
            for w in (icon_lbl, count_lbl, label_lbl, open_btn, top_row):
                try:
                    w.configure(bg=target_bg)
                except Exception:
                    pass

        def on_enter(e):
            _set_bg(hover_bg)

        def on_leave(e):
            _set_bg(BG_CARD)

        for w in [card, inner_wrap, inner, top_row, icon_lbl, count_lbl, label_lbl, open_btn]:
            w.bind("<Button-1>", lambda e, cmd=command: cmd())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        card._count_label = count_lbl  # type: ignore[attr-defined]
        return card

    def refresh_counts(self) -> None:
        counts = [
            len(fetch_employees_for_table()),
            len(fetch_students_for_table()),
            len(fetch_medicines_for_table()),
            len(fetch_appeals_for_table()),
        ]
        for i, card in enumerate(self.cards_frame.winfo_children()):
            try:
                card._count_label.configure(text=str(counts[i]))  # type: ignore[attr-defined]
            except Exception:
                pass
