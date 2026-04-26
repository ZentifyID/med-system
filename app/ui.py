import tkinter as tk
from tkinter import ttk
from typing import Any

# ── Color Palette ──────────────────────────────────────────────────────────────
# Sidebar (dark)
BG_SIDEBAR      = "#111827"
BG_SIDEBAR_ITEM_HOVER  = "#1F2937"
BG_SIDEBAR_ITEM_ACTIVE = "#1F2937"

# Content area
BG_COLOR        = "#F3F4F6"   # main content bg (light grey)
BG_CARD         = "#FFFFFF"   # card / panel bg
BG_COLOR_ALT    = "#F9FAFB"   # alternate rows

# Accent (indigo)
ACCENT          = "#6366F1"
ACCENT_HOVER    = "#4F46E5"
ACCENT_LIGHT    = "#EEF2FF"   # row hover / pill bg
ACCENT_FG       = "#FFFFFF"

# Text
TEXT_COLOR      = "#111827"
TEXT_MUTED      = "#6B7280"
TEXT_SIDEBAR    = "#9CA3AF"
TEXT_SIDEBAR_ACTIVE = "#FFFFFF"

# Form inputs
ENTRY_BG        = "#FFFFFF"
ENTRY_FG        = "#111827"
ENTRY_BORDER    = "#D1D5DB"
ENTRY_FOCUS     = "#6366F1"

# Danger
DANGER          = "#EF4444"
DANGER_HOVER    = "#DC2626"
DANGER_FG       = "#FFFFFF"

# Misc
BORDER          = "#E5E7EB"
SUCCESS         = "#10B981"
WARNING         = "#F59E0B"


class FlatButton(tk.Button):
    """Rounded-looking flat button with hover animation."""

    def __init__(self, master: tk.Misc, primary: bool = True, danger: bool = False, **kwargs: Any) -> None:
        self.primary = primary
        self.danger = danger

        if danger:
            self.default_bg   = DANGER
            self.hover_bg     = DANGER_HOVER
            self.default_fg   = DANGER_FG
        elif primary:
            self.default_bg   = ACCENT
            self.hover_bg     = ACCENT_HOVER
            self.default_fg   = ACCENT_FG
        else:
            self.default_bg   = "#FFFFFF"
            self.hover_bg     = "#F3F4F6"
            self.default_fg   = TEXT_COLOR

        kwargs.setdefault("bg", self.default_bg)
        kwargs.setdefault("fg", self.default_fg)
        kwargs.setdefault("activebackground", self.hover_bg)
        kwargs.setdefault("activeforeground", self.default_fg)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("font", ("Segoe UI", 10))
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 7)

        super().__init__(master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, _event: tk.Event) -> None:
        if self["state"] != tk.DISABLED:
            self.configure(bg=self.hover_bg)

    def on_leave(self, _event: tk.Event) -> None:
        self.configure(bg=self.default_bg)


class SidebarButton(tk.Frame):
    """Navigation button for the sidebar."""

    def __init__(
        self,
        master: tk.Misc,
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
            font=("Segoe UI", 13),
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR,
            width=2,
            anchor="center",
        )
        self._icon_label.pack(side=tk.LEFT, padx=(14, 4), pady=10)

        self._text_label = tk.Label(
            self,
            text=text,
            font=("Segoe UI", 10),
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR,
            anchor="w",
        )
        self._text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)

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
            # Left accent bar via padx shift
        else:
            bg = BG_SIDEBAR
            fg_icon = TEXT_SIDEBAR
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
        rowheight=36,
        fieldbackground=BG_CARD,
        font=("Segoe UI", 10),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=BG_CARD,
        foreground=TEXT_MUTED,
        font=("Segoe UI", 9, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(8, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT_LIGHT)],
        foreground=[("selected", TEXT_COLOR)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", BG_CARD)],
    )

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    style.configure(
        "Vertical.TScrollbar",
        background=BORDER,
        troughcolor=BG_CARD,
        borderwidth=0,
        arrowsize=14,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", TEXT_MUTED)],
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
