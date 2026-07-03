import tkinter as tk
from tkinter import ttk
from typing import Any

import customtkinter as ctk

from app.date_mask import DateMaskHandler
from app.hotkeys import setup_global_undo

from app.widgets import apply_combobox_patch

apply_combobox_patch()

# ── Палитра в стиле Linear (light) ───────────────────────────────────
# Sidebar: очень светлый серый, как у Linear, с тонкой правой границей
BG_SIDEBAR              = "#FAFAFA"
BG_SIDEBAR_ITEM_HOVER   = "#F0F0F1"
BG_SIDEBAR_ITEM_ACTIVE  = "#ECECEE"   # активный пункт — серый, как в Linear

# Content area: чисто белый
BG_COLOR        = "#FFFFFF"
BG_CARD         = "#FFFFFF"
BG_COLOR_ALT    = "#FAFAFB"

# Accent — фирменный индиго Linear
ACCENT          = "#5E6AD2"
ACCENT_HOVER    = "#5560C9"
ACCENT_LIGHT    = "#F0F1FB"
ACCENT_FG       = "#FFFFFF"

# Text
TEXT_COLOR      = "#282A30"
TEXT_MUTED      = "#8A8F98"
TEXT_SIDEBAR    = "#3C3F44"
TEXT_SIDEBAR_ACTIVE = "#18181B"

# Form inputs
ENTRY_BG        = "#FFFFFF"
ENTRY_FG        = "#282A30"
ENTRY_BORDER    = "#DEDEE1"
ENTRY_FOCUS     = "#5E6AD2"

# Danger
DANGER          = "#DC2626"
DANGER_HOVER    = "#B91C1C"
DANGER_FG       = "#FFFFFF"

# Misc: границы тоньше и светлее, как у Linear
BORDER          = "#E9E8EA"
SUCCESS         = "#0F9D58"
WARNING         = "#D97706"

# Sidebar border (thin right edge)
SIDEBAR_BORDER  = "#E9E8EA"

# Corner radius: компактнее, как у Linear
CORNER_RADIUS       = 8
MAIN_BUTTON_RADIUS  = 8

# Typography
FONT_FAMILY = "Segoe UI"
FONT_MEDIUM = "Segoe UI"


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
            self.hover_bg   = "#F4F4F5"
            self.text_col   = TEXT_COLOR

        # Initialize Frame
        super().__init__(
            master,
            fg_color=self.default_bg,
            corner_radius=kwargs.pop("corner_radius", CORNER_RADIUS),
            height=kwargs.pop("height", 38),
            width=kwargs.pop("width", 130),
            border_width=1 if not primary and not danger else 0,
            border_color=BORDER if not primary and not danger else None,
            cursor="hand2"
        )
        self.pack_propagate(False)
        self._state = "normal"

        # Label for text
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_MEDIUM, 13),
            text_color=self.text_col,
            fg_color="transparent"
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # Bindings
        for w in [self, self.label]:
            w.bind("<Button-1>", lambda e: self._on_click())
            w.bind("<Enter>", lambda e: self._on_enter())
            w.bind("<Leave>", lambda e: self._on_leave())

    def _on_click(self):
        if self._state == "normal" and self.command:
            self.command()

    def _on_enter(self):
        if self._state == "normal":
            self.configure(fg_color=self.hover_bg)

    def _on_leave(self):
        if self._state == "normal":
            self.configure(fg_color=self.default_bg)

    def set_state(self, state: str):
        self._state = state
        if state == "disabled":
            self.configure(fg_color="#E5E7EB", cursor="")
            self.label.configure(text_color="#9CA3AF")
        else:
            self.configure(fg_color=self.default_bg, cursor="hand2")
            self.label.configure(text_color=self.text_col)

    def configure_text(self, text: str):
        self.label.configure(text=text)


class SidebarButton(ctk.CTkFrame):
    """Custom sidebar button for perfect centering."""
    def __init__(self, master: Any, text: str = "", icon: Any = None, command: Any = None, **kwargs: Any) -> None:
        self.command = command
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=6,
            height=kwargs.pop("height", 34),
            cursor="hand2"
        )
        self.pack_propagate(False)
        self._active = False

        # Icon Label
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon if isinstance(icon, str) else "",
            image=icon if not isinstance(icon, str) else None,
            width=22,
            height=22,
            fg_color="transparent"
        )
        self.icon_label.place(x=12, rely=0.5, anchor="w")

        # Text Label
        self.text_label = ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_MEDIUM, 13),
            text_color=TEXT_SIDEBAR,
            fg_color="transparent"
        )
        self.text_label.place(x=44, rely=0.5, anchor="w")

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
            # Как в Linear: активный пункт — серая подложка, жирный тёмный текст
            self.configure(fg_color=BG_SIDEBAR_ITEM_ACTIVE)
            self.text_label.configure(text_color=TEXT_SIDEBAR_ACTIVE, font=(FONT_MEDIUM, 13, "bold"))
        else:
            self.configure(fg_color="transparent")
            self.text_label.configure(text_color=TEXT_SIDEBAR, font=(FONT_MEDIUM, 13))


def setup_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Treeview (Tables) — компактные строки, как списки в Linear ────────────
    style.configure(
        "Treeview",
        background=BG_CARD,
        foreground=TEXT_COLOR,
        rowheight=38,
        fieldbackground=BG_CARD,
        font=(FONT_FAMILY, 11),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=BG_CARD,
        foreground=TEXT_MUTED,
        font=(FONT_MEDIUM, 10),
        borderwidth=0,
        relief="flat",
        padding=(12, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT_LIGHT)],
        foreground=[("selected", TEXT_COLOR)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#F4F4F5")],
    )

    # ── Scrollbar — тонкий и незаметный ──────────────────────────────────────
    style.configure(
        "Vertical.TScrollbar",
        background="#E0E0E2",
        troughcolor="#FFFFFF",
        borderwidth=0,
        arrowsize=12,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#C9C9CC")],
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
        selectbackground=[("readonly", ENTRY_BG), ("focus", ENTRY_BG)],
        selectforeground=[("readonly", TEXT_COLOR), ("focus", TEXT_COLOR)],
        bordercolor=[("focus", ACCENT)],
    )

def show_toast(master: tk.Widget, message: str, type: str = "success") -> None:
    # В стиле Linear: тёмная плашка с цветной точкой-индикатором
    if type == "success": dot = "#4CB782"
    elif type == "error": dot = "#EB5757"
    elif type == "info": dot = "#4EA7FC"
    else: dot = "#8A8F98"

    toplevel = master.winfo_toplevel()
    toast = ctk.CTkFrame(toplevel, fg_color="#292A2E", corner_radius=8)
    row = tk.Frame(toast, bg="#292A2E")
    row.pack(padx=16, pady=10)
    tk.Label(row, text="●", font=(FONT_FAMILY, 10), bg="#292A2E", fg=dot).pack(side=tk.LEFT, padx=(0, 8))
    lbl = ctk.CTkLabel(row, text=message, font=(FONT_FAMILY, 12), text_color="#F7F8F8", fg_color="transparent")
    lbl.pack(side=tk.LEFT)
    
    # Place relative to bottom right
    toast.place(relx=1.0, rely=1.0, x=-36, y=-36, anchor="se")
    
    def fade_out(alpha=1.0):
        if not toast.winfo_exists(): return
        if alpha <= 0:
            toast.destroy()
            return
        # Tkinter frame transparency isn't perfectly supported via place, 
        # so we just destroy it after a delay.
        pass

    def destroy_toast():
        if toast.winfo_exists():
            toast.destroy()
            
    toplevel.after(3000, destroy_toast)


def sort_treeview_column(tv: ttk.Treeview, col: str, reverse: bool) -> None:
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    
    from datetime import datetime
    def parse_val(val):
        if not val: return 0
        if len(val) == 10 and val.count(".") == 2:
            try: return datetime.strptime(val, "%d.%m.%Y").timestamp()
            except ValueError: pass
        try: return float(val)
        except ValueError: return val.lower()

    l.sort(key=lambda t: parse_val(t[0]), reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
        current_tags = list(tv.item(k, "tags"))
        base_tags = [t for t in current_tags if t not in ("odd", "even")]
        if not base_tags:
            base_tags.append("odd" if index % 2 == 0 else "even")
        tv.item(k, tags=tuple(base_tags))

    tv.heading(col, command=lambda _col=col: sort_treeview_column(tv, _col, not reverse))


class ICDAutocomplete:
    def __init__(self, entry: ctk.CTkEntry, var: tk.StringVar, search_callback):
        self.entry = entry
        self.var = var
        self.search_callback = search_callback
        self.popup = None
        self.listbox = None
        self._after_id = None
        
        # Bind keys on both ctk wrapper and underlying _entry
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<FocusIn>", self._on_key_release)
        self.entry.bind("<Down>", self._on_arrow_down)
        self.entry.bind("<Escape>", self._on_escape)
        
        if hasattr(self.entry, "_entry"):
            self.entry._entry.bind("<KeyRelease>", self._on_key_release)
            self.entry._entry.bind("<FocusOut>", self._on_focus_out)
            self.entry._entry.bind("<FocusIn>", self._on_key_release)
            self.entry._entry.bind("<Down>", self._on_arrow_down)
            self.entry._entry.bind("<Escape>", self._on_escape)

    def _on_key_release(self, event=None):
        if event and event.keysym in ("Down", "Up", "Return", "Escape"):
            return
            
        val = self.var.get().strip().lower()
        if not val:
            self._hide_suggestions()
            return
            
        # Fetch matching items from the decoupled callback
        matches = self.search_callback(val)
                
        if matches:
            self._show_suggestions(matches)
        else:
            self._hide_suggestions()

    def _show_suggestions(self, matches):
        if self._after_id:
            self.entry.after_cancel(self._after_id)
            self._after_id = None
            
        if not self.popup:
            self.popup = tk.Toplevel(self.entry.winfo_toplevel())
            self.popup.wm_overrideredirect(True)
            self.popup.configure(bg=BORDER)
            
            frame = tk.Frame(self.popup, bg="white")
            frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
            
            scrollbar = tk.Scrollbar(frame, orient="vertical")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.listbox = tk.Listbox(
                frame,
                font=(FONT_FAMILY, 11),
                bg="white",
                fg=TEXT_COLOR,
                selectbackground=ACCENT,
                selectforeground="white",
                bd=0, 
                highlightthickness=0,
                activestyle="none",
                yscrollcommand=scrollbar.set
            )
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.listbox.yview)
            
            self.listbox.bind("<ButtonRelease-1>", self._on_select)
            self.listbox.bind("<Return>", self._on_select)
            self.listbox.bind("<Escape>", self._on_escape)
            self.listbox.bind("<FocusOut>", self._on_focus_out)
            
        self.listbox.delete(0, tk.END)
        for item in matches:
            display_text = f"{item['code']} - {item['name']}"
            self.listbox.insert(tk.END, display_text)
            
        self.entry.update_idletasks()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()
        height = min(150, len(matches) * 24 + 4)
        
        self.popup.geometry(f"{width}x{height}+{x}+{y}")
        self.popup.deiconify()
        self.popup.lift()

    def _hide_suggestions(self):
        if self.popup:
            self.popup.withdraw()

    def _on_focus_out(self, event):
        if self._after_id:
            self.entry.after_cancel(self._after_id)
        self._after_id = self.entry.after(200, self._delayed_hide)

    def _delayed_hide(self):
        focus = self.entry.focus_get()
        if self.popup and focus != self.listbox and focus != self.popup:
            self._hide_suggestions()

    def _on_arrow_down(self, event):
        if self.popup and self.listbox and self.listbox.size() > 0:
            self.listbox.focus_set()
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(0)
            self.listbox.activate(0)
            return "break"

    def _on_escape(self, event=None):
        self._hide_suggestions()
        self.entry.focus_set()
        return "break"

    def _on_select(self, event=None):
        if not self.listbox:
            return
        idx = self.listbox.curselection()
        if idx:
            selected_text = self.listbox.get(idx[0])
            self.var.set(selected_text)
            self._hide_suggestions()
            self.entry.focus_set()
            if hasattr(self.entry, "_entry"):
                self.entry._entry.icursor(tk.END)
            else:
                self.entry.icursor(tk.END)
