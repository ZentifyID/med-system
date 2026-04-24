import tkinter as tk
from typing import Any

# Color Palette
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#18181B"
TEXT_MUTED = "#71717A"

BTN_PRIMARY_BG = "#18181B"
BTN_PRIMARY_FG = "#FFFFFF"
BTN_PRIMARY_HOVER = "#3F3F46"

BTN_SECONDARY_BG = "#F4F4F5"
BTN_SECONDARY_FG = "#18181B"
BTN_SECONDARY_HOVER = "#E4E4E7"

ENTRY_BG = "#FFFFFF"
ENTRY_FG = "#18181B"
ENTRY_BORDER = "#E4E4E7"
ENTRY_FOCUS = "#52525B"


class FlatButton(tk.Button):
    def __init__(self, master: tk.Misc, primary: bool = True, **kwargs: Any) -> None:
        self.primary = primary
        self.default_bg = BTN_PRIMARY_BG if primary else BTN_SECONDARY_BG
        self.hover_bg = BTN_PRIMARY_HOVER if primary else BTN_SECONDARY_HOVER
        self.default_fg = BTN_PRIMARY_FG if primary else BTN_SECONDARY_FG

        kwargs.setdefault("bg", self.default_bg)
        kwargs.setdefault("fg", self.default_fg)
        kwargs.setdefault("activebackground", self.hover_bg)
        kwargs.setdefault("activeforeground", self.default_fg)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("font", ("Segoe UI", 10))
        kwargs.setdefault("cursor", "hand2")

        super().__init__(master, **kwargs)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, _event: tk.Event) -> None:
        if self["state"] != tk.DISABLED:
            self.configure(bg=self.hover_bg)

    def on_leave(self, _event: tk.Event) -> None:
        self.configure(bg=self.default_bg)


def setup_styles(root: tk.Tk) -> None:
    from tkinter import ttk
    
    style = ttk.Style(root)
    # Use clam theme which supports flat styles and custom backgrounds easily
    style.theme_use("clam")
    
    # Treeview styling
    style.configure(
        "Treeview",
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        rowheight=34,
        fieldbackground=BG_COLOR,
        font=("Segoe UI", 10),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=BG_COLOR,
        foreground=TEXT_MUTED,
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", "#F4F4F5")],
        foreground=[("selected", TEXT_COLOR)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", BG_COLOR)],
    )
    
    # Combobox styling
    style.configure(
        "TCombobox",
        fieldbackground=BG_COLOR,
        background=BG_COLOR,
        foreground=TEXT_COLOR,
        bordercolor=ENTRY_BORDER,
        arrowcolor=TEXT_COLOR,
        font=("Segoe UI", 10),
    )
