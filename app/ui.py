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
CORNER_RADIUS       = 10
MAIN_BUTTON_RADIUS  = 25

# Typography
FONT_FAMILY = "Google Sans"
FONT_MEDIUM = "Google Sans Medium"


class FlatButton(ctk.CTkFrame):
    """Custom button using CTkFrame + CTkLabel for perfect font centering."""
    def __init__(self, master: Any, text: str = "", command: Any = None, primary: bool = True, danger: bool = False, **kwargs: Any) -> None:
        self.command = command
        self.primary = primary
        self.danger = danger
        
        # Determine colors
        if danger:
            self.default_bg = DANGER
            self.hover_bg   = DANGER_HOVER
            self.text_col   = DANGER_FG
        elif primary:
            self.default_bg = ACCENT
            self.hover_bg   = ACCENT_HOVER
            self.text_col   = ACCENT_FG
        else:
            self.default_bg = "#FFFFFF"
            self.hover_bg   = "#F3F4F6"
            self.text_col   = TEXT_COLOR

        # Initialize Frame
        super().__init__(
            master,
            fg_color=self.default_bg,
            corner_radius=kwargs.pop("corner_radius", CORNER_RADIUS),
            height=kwargs.pop("height", 48),
            width=kwargs.pop("width", 140),
            border_width=1 if not primary and not danger else 0,
            border_color=BORDER if not primary and not danger else None,
            cursor="hand2"
        )
        self.pack_propagate(False)

        # Label for text
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_MEDIUM, 15),
            text_color=self.text_col,
            fg_color="transparent"
        )
        self.label.place(relx=0.5, rely=0.55, anchor="center")

        # Bindings
        for w in [self, self.label]:
            w.bind("<Button-1>", lambda e: self._on_click())
            w.bind("<Enter>", lambda e: self._on_enter())
            w.bind("<Leave>", lambda e: self._on_leave())

    def _on_click(self):
        if self.command:
            self.command()

    def _on_enter(self):
        self.configure(fg_color=self.hover_bg)

    def _on_leave(self):
        self.configure(fg_color=self.default_bg)

    def configure_text(self, text: str):
        self.label.configure(text=text)


class SidebarButton(ctk.CTkFrame):
    """Custom sidebar button for perfect centering."""
    def __init__(self, master: Any, text: str = "", icon: Any = None, command: Any = None, **kwargs: Any) -> None:
        self.command = command
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=CORNER_RADIUS,
            height=kwargs.pop("height", 44),
            cursor="hand2"
        )
        self.pack_propagate(False)
        self._active = False

        # Icon Label
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon if isinstance(icon, str) else "",
            image=icon if not isinstance(icon, str) else None,
            width=24,
            height=24,
            fg_color="transparent"
        )
        self.icon_label.place(x=16, rely=0.5, anchor="w")

        # Text Label
        self.text_label = ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_MEDIUM, 15),
            text_color=TEXT_SIDEBAR,
            fg_color="transparent"
        )
        self.text_label.place(x=52, rely=0.57, anchor="w")

        # Bindings
        for w in [self, self.icon_label, self.text_label]:
            w.bind("<Button-1>", lambda e: self._on_click())
            w.bind("<Enter>", lambda e: self._on_enter())
            w.bind("<Leave>", lambda e: self._on_leave())

    def _on_click(self):
        if self.command:
            self.command()

    def _on_enter(self):
        if not self._active:
            self.configure(fg_color=BG_SIDEBAR_ITEM_HOVER)

    def _on_leave(self):
        if not self._active:
            self.configure(fg_color="transparent")

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self.configure(fg_color=BG_SIDEBAR_ITEM_ACTIVE)
            self.text_label.configure(text_color=TEXT_SIDEBAR_ACTIVE)
        else:
            self.configure(fg_color="transparent")
            self.text_label.configure(text_color=TEXT_SIDEBAR)


def setup_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Treeview (Tables) ──────────────────────────────────────────────────────
    style.configure(
        "Treeview",
        background=BG_CARD,
        foreground=TEXT_COLOR,
        rowheight=42,
        fieldbackground=BG_CARD,
        font=(FONT_FAMILY, 11),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background="#F9FAFB",
        foreground=TEXT_MUTED,
        font=(FONT_MEDIUM, 10),
        borderwidth=0,
        relief="flat",
        padding=(12, 10),
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
