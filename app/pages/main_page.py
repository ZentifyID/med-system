"""Главная страница с карточками разделов."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Any

import customtkinter as ctk

from app.ui import (
    BG_CARD, BG_COLOR, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_FG, ACCENT_LIGHT,
    BORDER, CORNER_RADIUS, MAIN_BUTTON_RADIUS, FONT_FAMILY, FONT_MEDIUM, FlatButton,
)
from app.db import (
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
        icons: dict | None = None,
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
        self._icons = icons or {}

        # Header
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=36, pady=(36, 4))

        tk.Label(
            header,
            text="Главная",
            font=(FONT_FAMILY, 19, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="Обзор системы",
            font=(FONT_FAMILY, 12),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        ).pack(side=tk.LEFT, padx=(14, 0), pady=(4, 0))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(8, 28))

        # Stats cards row
        self.cards_frame = tk.Frame(self, bg=BG_COLOR)
        self.cards_frame.pack(fill=tk.X, padx=36, pady=(0, 32))

        card_defs = [
            (self._icons.get("employees", "👤"), "Сотрудники", "0", on_employees),
            (self._icons.get("students", "🎓"), "Студенты", "0", on_students),
            (self._icons.get("medicine", "💊"), "Лекарства", "0", on_medicines),
            (self._icons.get("appeals", "📋"), "Обращения", "0", on_appeals),
        ]

        for i, (icon, label, count, cmd) in enumerate(card_defs):
            card = self._build_stat_card(self.cards_frame, icon, label, count, cmd)
            card.grid(row=0, column=i, padx=(0, 16) if i < 3 else 0, sticky="nsew")
            self.cards_frame.grid_columnconfigure(i, weight=1)

        # Quick action section
        tk.Label(
            self,
            text="Быстрый доступ",
            font=(FONT_FAMILY, 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(anchor="w", padx=36, pady=(0, 14))

        actions_frame = tk.Frame(self, bg=BG_COLOR)
        actions_frame.pack(fill=tk.X, padx=36)

        quick_buttons = [
            ("Добавить сотрудника", self._on_add_employee),
            ("Добавить студента",   self._on_add_student),
            ("Добавить лекарство",  self._on_add_medicine),
            ("Новое обращение",    self._on_add_appeal),
        ]

        for i, (text, cmd) in enumerate(quick_buttons):
            btn = FlatButton(
                actions_frame,
                primary=True,
                text=text,
                command=cmd,
                corner_radius=CORNER_RADIUS,
                height=44,
            )
            btn.grid(row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="ew")
            actions_frame.grid_columnconfigure(i, weight=1)

    def _build_stat_card(
        self,
        parent: tk.Frame,
        icon: Any,
        label: str,
        count: str,
        command: Callable,
    ) -> ctk.CTkFrame:
        # Card using CTkFrame for rounded corners
        card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            border_color=BORDER,
            border_width=1,
            corner_radius=10,
            cursor="hand2"
        )

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)

        # Icon + count row
        top_row = tk.Frame(inner, bg=BG_CARD)
        top_row.pack(fill=tk.X)

        icon_lbl = ctk.CTkLabel(
            top_row,
            text=icon if isinstance(icon, str) else "",
            image=icon if not isinstance(icon, str) else None,
            font=(FONT_FAMILY, 20),
            text_color=TEXT_COLOR,
            anchor="center",
            width=32,
            height=32,
        )
        icon_lbl.pack(side=tk.LEFT)

        count_lbl = ctk.CTkLabel(
            top_row,
            text=count,
            font=(FONT_FAMILY, 24, "bold"),
            fg_color="transparent",
            text_color=TEXT_COLOR
        )
        count_lbl.pack(side=tk.RIGHT)

        # Label
        label_lbl = ctk.CTkLabel(
            inner,
            text=label,
            font=(FONT_FAMILY, 14),
            fg_color="transparent",
            text_color=TEXT_MUTED
        )
        label_lbl.pack(anchor="w", pady=(6, 2))

        # Click link
        open_btn = ctk.CTkLabel(
            inner,
            text="Открыть →",
            font=(FONT_FAMILY, 12),
            fg_color="transparent",
            text_color=ACCENT,
            cursor="hand2",
        )
        open_btn.pack(anchor="w")

        # Hover — едва заметный, как у Linear
        hover_bg = "#FAFAFA"

        def _set_bg(target_bg):
            card.configure(fg_color=target_bg)
            inner.configure(bg=target_bg)
            top_row.configure(bg=target_bg)

        def on_enter(e):
            _set_bg(hover_bg)

        def on_leave(e):
            _set_bg(BG_CARD)

        for w in [card, inner, top_row, icon_lbl, count_lbl, label_lbl, open_btn]:
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
