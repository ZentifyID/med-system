import tkinter as tk
from tkinter import ttk
from typing import Callable, Any

import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, ACCENT, ACCENT_LIGHT,
    BORDER, ENTRY_BG, ENTRY_FG, ENTRY_BORDER, CORNER_RADIUS, FlatButton,
    FONT_FAMILY, FONT_MEDIUM, sort_treeview_column
)


def _make_section_header(parent: tk.Frame, title: str, btn_text: str, btn_cmd: Callable, btn2_text: str | None = None, btn2_cmd: Callable | None = None) -> None:
    row = tk.Frame(parent, bg=BG_COLOR)
    row.pack(fill=tk.X, padx=36, pady=(32, 0))
    tk.Label(row, text=title, font=(FONT_FAMILY, 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
    FlatButton(row, primary=True, text=btn_text, command=btn_cmd, height=44, width=160).pack(side=tk.RIGHT)
    if btn2_text and btn2_cmd:
        FlatButton(row, primary=False, text=btn2_text, command=btn2_cmd, height=44, width=180).pack(side=tk.RIGHT, padx=(0, 12))
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=36, pady=(16, 0))


def _make_search_bar(parent: tk.Frame, search_var: tk.StringVar, filter_var: tk.StringVar | None, filter_values: list[str] | None, trigger_fn: Callable, search_icon: Any = None) -> ctk.CTkEntry:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(20, 16))

    if search_icon:
        icon_label = ctk.CTkLabel(bar, text="", image=search_icon, width=24, height=24)
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
    else:
        # Fallback if icon is missing
        icon_label = ctk.CTkLabel(bar, text="🔍", font=(FONT_FAMILY, 16), text_color=TEXT_MUTED)
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

    search_entry = ctk.CTkEntry(
        bar,
        textvariable=search_var,
        font=(FONT_FAMILY, 14),
        fg_color=BG_CARD,
        text_color=TEXT_COLOR,
        border_color=ENTRY_BORDER,
        corner_radius=CORNER_RADIUS,
        placeholder_text="Поиск...",
        placeholder_text_color=TEXT_MUTED,
        height=44,
    )
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    parent.search_entry = search_entry

    if filter_var and filter_values:
        combo = ctk.CTkComboBox(
            bar, variable=filter_var, state="readonly", values=filter_values, width=200,
            font=(FONT_FAMILY, 14), dropdown_font=(FONT_FAMILY, 12),
            fg_color=ENTRY_BG, text_color=ENTRY_FG, border_color=ENTRY_BORDER,
            button_color=ENTRY_BORDER, button_hover_color=ACCENT, corner_radius=CORNER_RADIUS, height=44,
            command=trigger_fn
        )
        combo.pack(side=tk.RIGHT)

    return search_entry


def _make_table_card(parent: tk.Frame, columns: tuple, headings: dict, widths: dict, anchors: dict | None = None) -> tuple[tk.Frame, ttk.Treeview]:
    # Modern card container for table
    card = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        border_color=BORDER,
        border_width=1,
        corner_radius=12
    )
    card.pack(fill=tk.BOTH, expand=True, padx=36, pady=(0, 20))

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    tv = ttk.Treeview(inner, columns=columns, show="headings")
    for col in columns:
        tv.heading(col, text=headings.get(col, col), command=lambda c=col: sort_treeview_column(tv, c, False))
        anchor = (anchors or {}).get(col, tk.W)
        tv.column(col, width=widths.get(col, 150), anchor=anchor, stretch=True)

    tv.tag_configure("odd", background=BG_CARD)
    tv.tag_configure("even", background="#F9FAFB")

    sb = ttk.Scrollbar(inner, orient=tk.VERTICAL, command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    def on_right_click(event):
        item = tv.identify_row(event.y)
        if item:
            tv.selection_set(item)
            menu = tk.Menu(parent, tearoff=0, font=(FONT_FAMILY, 10))
            if hasattr(parent, "_open_selected"):
                menu.add_command(label="Открыть / Редактировать", command=parent._open_selected)
            if hasattr(parent, "_copy_fio"):
                menu.add_command(label="Скопировать основное значение", command=parent._copy_fio)
            if hasattr(parent, "on_delete_cb"):
                menu.add_separator()
                menu.add_command(label="Удалить", command=lambda: parent.on_delete_cb(int(item)))
            menu.tk_popup(event.x_root, event.y_root)

    tv.bind("<Button-3>", on_right_click)
    
    return card, tv


def _make_action_bar(parent: tk.Frame, buttons: list[tuple[str, bool, Callable]]) -> tk.Frame:
    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill=tk.X, padx=36, pady=(0, 32))
    for i, (text, primary, cmd) in enumerate(buttons):
        FlatButton(bar, primary=primary, text=text, command=cmd, height=44, width=120).pack(side=tk.LEFT, padx=(0 if i == 0 else 12, 0))
    return bar
