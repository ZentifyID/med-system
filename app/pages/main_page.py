import tkinter as tk
from tkinter import ttk
from typing import Callable

from app.ui import (
    BG_CARD, BG_COLOR, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_FG,
    BORDER, SUCCESS, WARNING, DANGER,
    FlatButton,
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
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_employees = on_employees
        self._on_students = on_students
        self._on_medicines = on_medicines
        self._on_appeals = on_appeals

        # Header
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=32, pady=(32, 8))

        tk.Label(
            header,
            text="Главная",
            font=("Segoe UI", 22, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="Обзор системы",
            font=("Segoe UI", 12),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        ).pack(side=tk.LEFT, padx=(16, 0), pady=(6, 0))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X, padx=32, pady=(0, 24))

        # Stats cards row
        self.cards_frame = tk.Frame(self, bg=BG_COLOR)
        self.cards_frame.pack(fill=tk.X, padx=32, pady=(0, 24))

        self._stat_cards: list[dict] = []

        card_defs = [
            ("👤", "Сотрудники", "0", ACCENT, on_employees),
            ("🎓", "Студенты", "0", "#8B5CF6", on_students),
            ("💊", "Лекарства", "0", SUCCESS, on_medicines),
            ("📋", "Обращения", "0", WARNING, on_appeals),
        ]

        for i, (icon, label, count, color, cmd) in enumerate(card_defs):
            card = self._build_stat_card(self.cards_frame, icon, label, count, color, cmd)
            card.grid(row=0, column=i, padx=(0, 16) if i < 3 else 0, sticky="ew")
            self.cards_frame.grid_columnconfigure(i, weight=1)
            self._stat_cards.append({"label": label, "color": color})

        # Quick action section
        tk.Label(
            self,
            text="Быстрый доступ",
            font=("Segoe UI", 14, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(anchor="w", padx=32, pady=(0, 16))

        actions_frame = tk.Frame(self, bg=BG_COLOR)
        actions_frame.pack(fill=tk.X, padx=32)

        quick_buttons = [
            ("+ Добавить сотрудника", on_employees),
            ("+ Добавить студента", on_students),
            ("+ Добавить лекарство", on_medicines),
            ("+ Новое обращение", on_appeals),
        ]

        for i, (text, cmd) in enumerate(quick_buttons):
            btn = FlatButton(
                actions_frame,
                primary=True,
                text=text,
                command=cmd,
                font=("Segoe UI", 10),
            )
            btn.grid(row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="ew")
            actions_frame.grid_columnconfigure(i, weight=1)

    def _build_stat_card(
        self,
        parent: tk.Frame,
        icon: str,
        label: str,
        count: str,
        color: str,
        command: Callable,
    ) -> tk.Frame:
        card = tk.Frame(parent, bg=BG_CARD, cursor="hand2", bd=0)
        card.configure(relief="flat")

        # Top color bar
        bar = tk.Frame(card, bg=color, height=4)
        bar.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Icon + count row
        top_row = tk.Frame(inner, bg=BG_CARD)
        top_row.pack(fill=tk.X)

        icon_lbl = tk.Label(top_row, text=icon, font=("Segoe UI", 22), bg=BG_CARD, fg=color)
        icon_lbl.pack(side=tk.LEFT)

        count_lbl = tk.Label(top_row, text=count, font=("Segoe UI", 28, "bold"), bg=BG_CARD, fg=TEXT_COLOR)
        count_lbl.pack(side=tk.RIGHT)

        # Label
        tk.Label(inner, text=label, font=("Segoe UI", 11), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(8, 4))

        # Click action
        open_btn = tk.Label(
            inner,
            text="Открыть →",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=color,
            cursor="hand2",
        )
        open_btn.pack(anchor="w")

        # Hover effects
        def on_enter(e):
            card.configure(bg="#F8FAFF")
            inner.configure(bg="#F8FAFF")
            for w in inner.winfo_children():
                try:
                    w.configure(bg="#F8FAFF")
                except Exception:
                    pass
            for row in inner.winfo_children():
                try:
                    for w in row.winfo_children():
                        w.configure(bg="#F8FAFF")
                except Exception:
                    pass

        def on_leave(e):
            card.configure(bg=BG_CARD)
            inner.configure(bg=BG_CARD)
            for w in inner.winfo_children():
                try:
                    w.configure(bg=BG_CARD)
                except Exception:
                    pass
            for row in inner.winfo_children():
                try:
                    for w in row.winfo_children():
                        w.configure(bg=BG_CARD)
                except Exception:
                    pass

        for widget in [card, bar, inner, top_row, icon_lbl, count_lbl, open_btn]:
            widget.bind("<Button-1>", lambda e, cmd=command: cmd())
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # Store count label reference on card for later update
        card._count_label = count_lbl  # type: ignore[attr-defined]
        return card

    def refresh_counts(self) -> None:
        """Update stat card counts from DB."""
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
