import tkinter as tk
from tkinter import ttk
from typing import Any

import customtkinter as ctk

# ── Color Palette — Closure‑style Clean Light UI ─────────────────────────────
# Sidebar (white with right border)
BG_SIDEBAR              = "#FFFFFF"
BG_SIDEBAR_ITEM_HOVER   = "#F3F4F6"
BG_SIDEBAR_ITEM_ACTIVE  = "#EEF2FF"   # soft indigo tint

# Content area
BG_COLOR        = "#F7F8FA"   # very light warm grey
BG_CARD         = "#FFFFFF"
BG_COLOR_ALT    = "#F9FAFB"

# Accent – soft indigo (matches Closure's purple/indigo active state)
ACCENT          = "#4F46E5"
ACCENT_HOVER    = "#4338CA"
ACCENT_LIGHT    = "#EEF2FF"
ACCENT_FG       = "#FFFFFF"

# Text
TEXT_COLOR      = "#111827"
TEXT_MUTED      = "#6B7280"
TEXT_SIDEBAR    = "#374151"
TEXT_SIDEBAR_ACTIVE = "#4F46E5"

# Form inputs
ENTRY_BG        = "#FFFFFF"
ENTRY_FG        = "#111827"
ENTRY_BORDER    = "#D1D5DB"
ENTRY_FOCUS     = "#4F46E5"

# Danger
DANGER          = "#DC2626"
DANGER_HOVER    = "#B91C1C"
DANGER_FG       = "#FFFFFF"

# Misc
BORDER          = "#E5E7EB"
SUCCESS         = "#059669"
WARNING         = "#D97706"

# Sidebar border (thin right edge)
SIDEBAR_BORDER  = "#E5E7EB"

# Corner radius for customtkinter widgets
CORNER_RADIUS   = 10


class FlatButton(ctk.CTkButton):
    """Rounded flat button using customtkinter."""

    def __init__(self, master: Any, primary: bool = True, danger: bool = False, **kwargs: Any) -> None:
        if danger:
            default_bg   = DANGER
            hover_bg     = DANGER_HOVER
            default_fg   = DANGER_FG
        elif primary:
            default_bg   = ACCENT
            hover_bg     = ACCENT_HOVER
            default_fg   = ACCENT_FG
        else:
            default_bg   = "#FFFFFF"
            hover_bg     = "#F3F4F6"
            default_fg   = TEXT_COLOR

        kwargs.setdefault("fg_color", default_bg)
        kwargs.setdefault("hover_color", hover_bg)
        kwargs.setdefault("text_color", default_fg)
        kwargs.setdefault("corner_radius", CORNER_RADIUS)
        kwargs.setdefault("font", ctk.CTkFont(family="Segoe UI", size=13))
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("height", 36)

        if not primary and not danger:
            kwargs.setdefault("border_width", 1)
            kwargs.setdefault("border_color", BORDER)

        super().__init__(master, **kwargs)


class SidebarButton(tk.Frame):
    """Closure-style sidebar nav button — clean text with icon, rounded active pill."""

    def __init__(
        self,
        master: Any,
        text: str,
        icon: str = "",
        command: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=BG_SIDEBAR, cursor="hand2", **kwargs)
        self._command = command
        self._active = False

        self._icon_label = tk.Label(
            self,
            text=icon,
            font=("Segoe UI", 11),
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            width=2,
            anchor="center",
        )
        self._icon_label.pack(side=tk.LEFT, padx=(12, 6), pady=8)

        self._text_label = tk.Label(
            self,
            text=text,
            font=("Segoe UI", 10),
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR,
            anchor="w",
        )
        self._text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 12))

        for widget in (self, self._icon_label, self._text_label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, _event: tk.Event) -> None:
        if self._command:
            self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        if not self._active:
            for w in (self, self._icon_label, self._text_label):
                w.configure(bg=BG_SIDEBAR_ITEM_HOVER)

    def _on_leave(self, _event: tk.Event) -> None:
        if not self._active:
            for w in (self, self._icon_label, self._text_label):
                w.configure(bg=BG_SIDEBAR)

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            bg = BG_SIDEBAR_ITEM_ACTIVE
            fg_icon = ACCENT
            fg_text = TEXT_SIDEBAR_ACTIVE
        else:
            bg = BG_SIDEBAR
            fg_icon = TEXT_MUTED
            fg_text = TEXT_SIDEBAR

        for w in (self, self._icon_label, self._text_label):
            w.configure(bg=bg)
        self._icon_label.configure(fg=fg_icon)
        self._text_label.configure(fg=fg_text)


def setup_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure(
        "Treeview",
        background=BG_CARD,
        foreground=TEXT_COLOR,
        rowheight=38,
        fieldbackground=BG_CARD,
        font=("Segoe UI", 10),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background="#F9FAFB",
        foreground=TEXT_MUTED,
        font=("Segoe UI", 9, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(10, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT_LIGHT)],
        foreground=[("selected", TEXT_COLOR)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#F3F4F6")],
    )

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    style.configure(
        "Vertical.TScrollbar",
        background="#D1D5DB",
        troughcolor="#F9FAFB",
        borderwidth=0,
        arrowsize=14,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#9CA3AF")],
    )

    # ── Combobox ──────────────────────────────────────────────────────────────
    style.configure(
        "TCombobox",
        fieldbackground=ENTRY_BG,
        background=ENTRY_BG,
        foreground=TEXT_COLOR,
        bordercolor=ENTRY_BORDER,
        arrowcolor=TEXT_MUTED,
        font=("Segoe UI", 10),
        padding=(8, 6),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", ENTRY_BG)],
        bordercolor=[("focus", ACCENT)],
    )
