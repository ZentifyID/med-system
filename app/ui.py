import tkinter as tk
from tkinter import ttk
from typing import Any
from collections import deque

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
        self._state = "normal"

        # Label for text
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_MEDIUM, 15),
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
        self.text_label.place(x=52, rely=0.5, anchor="w")

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
        selectbackground=[("readonly", ENTRY_BG), ("focus", ENTRY_BG)],
        selectforeground=[("readonly", TEXT_COLOR), ("focus", TEXT_COLOR)],
        bordercolor=[("focus", ACCENT)],
    )

class DateMaskHandler:
    """Инкапсулирует логику форматирования и обработки ввода дат (маска ДД.ММ.ГГГГ)."""
    
    @staticmethod
    def bind_to_entry(entry_widget: tk.Widget | ctk.CTkEntry, string_var: tk.StringVar) -> None:
        inner_entry = entry_widget._entry if hasattr(entry_widget, '_entry') else entry_widget
        handler = DateMaskHandler(inner_entry, string_var)
        
        inner_entry.bind("<FocusIn>", handler.on_focus_in)
        inner_entry.bind("<FocusOut>", handler.on_focus_out)
        inner_entry.bind("<KeyPress>", handler.on_keypress)
        inner_entry.bind("<Control-v>", handler.on_paste)
        inner_entry.bind("<<Paste>>", handler.on_paste)

    def __init__(self, entry: tk.Widget, var: tk.StringVar):
        self.entry = entry
        self.var = var

    def on_focus_in(self, event: tk.Event) -> None:
        if self.var.get() == "__.__.____":
            self.var.set("")

    def on_focus_out(self, event: tk.Event) -> None:
        if not self.var.get().strip():
            self.var.set("__.__.____")

    def _fmt(self, digits: str) -> str:
        if len(digits) <= 2:
            return digits
        if len(digits) <= 4:
            return f"{digits[:2]}.{digits[2:]}"
        return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"

    def _d2i(self, display: str, idx: int) -> int:
        return sum(1 for c in display[:idx] if c.isdigit())

    def _i2d(self, i: int) -> int:
        if i <= 2:
            return i
        if i <= 4:
            return i + 1
        return i + 2

    def _digits(self, v: str) -> str:
        return "".join(c for c in v if c.isdigit())[:8]

    def _replace(self, digits: str, s: int, e: int, r: str = "") -> str:
        return (digits[:s] + r + digits[e:])[:8]

    def _apply(self, digits: str, caret: int) -> str:
        digits = digits[:8]
        self.var.set(self._fmt(digits))
        self.entry.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def on_keypress(self, ev: tk.Event) -> str | None:
        cur = self.entry.get()
        if cur == "__.__.____":
            cur = ""
        digits = self._digits(cur)
        has_sel = self.entry.selection_present()
        
        if has_sel:
            s = self._d2i(cur, self.entry.index("sel.first"))
            en = self._d2i(cur, self.entry.index("sel.last"))
        else:
            s = en = self._d2i(cur, self.entry.index(tk.INSERT))
            
        ctrl = bool(ev.state & 0x4)
        if ctrl and ev.keysym.lower() in {"a", "c", "x"}:
            return None
        if ctrl and ev.keysym.lower() == "v":
            return self.on_paste(ev)
        if ev.keysym in {"Left", "Right", "Home", "End", "Tab", "ISO_Left_Tab", "Shift_L", "Shift_R"}:
            return None
            
        if ev.keysym == "BackSpace":
            if has_sel:
                return self._apply(self._replace(digits, s, en), s)
            if s == 0:
                return "break"
            return self._apply(self._replace(digits, s - 1, s), s - 1)
            
        if ev.keysym == "Delete":
            if has_sel:
                return self._apply(self._replace(digits, s, en), s)
            if s >= len(digits):
                return "break"
            return self._apply(self._replace(digits, s, s + 1), s)
            
        if ev.char.isdigit():
            if len(digits) >= 8 and not has_sel:
                return "break"
            return self._apply(self._replace(digits, s, en, ev.char), s + 1)
            
        return "break"

    def on_paste(self, event: tk.Event) -> str:
        cur = self.entry.get()
        if cur == "__.__.____":
            cur = ""
        digits = self._digits(cur)
        
        try:
            cb = self.entry.clipboard_get()
        except tk.TclError:
            return "break"
            
        pd = "".join(c for c in cb if c.isdigit())
        if not pd:
            return "break"
            
        has_sel = self.entry.selection_present()
        if has_sel:
            s = self._d2i(cur, self.entry.index("sel.first"))
            en = self._d2i(cur, self.entry.index("sel.last"))
        else:
            s = en = self._d2i(cur, self.entry.index(tk.INSERT))
            
        nd = self._replace(digits, s, en, pd)
        return self._apply(nd, min(s + len(pd), len(nd)))

def setup_global_undo(root: tk.Tk) -> None:
    def get_stacks(w: tk.Widget) -> tuple[deque, deque]:
        if not hasattr(w, "_undo_stack"):
            w._undo_stack = deque(maxlen=50)
            w._redo_stack = deque(maxlen=50)
            w._last_val = w.get() if hasattr(w, "get") else ""
        return w._undo_stack, w._redo_stack

    def track_changes(event: tk.Event) -> None:
        w = getattr(event, "widget", None)
        if not isinstance(w, tk.Entry):
            return
        keysym = getattr(event, "keysym", "")
        if keysym in ('Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R'):
            return
        state = getattr(event, "state", 0)
        if state & 0x0004 and keysym.lower() in ('z', 'y', 'я', 'н'):
            return
            
        undo_stack, redo_stack = get_stacks(w)
        try:
            cur = w.get()
        except Exception:
            return
        if cur != w._last_val:
            undo_stack.append(w._last_val)
            redo_stack.clear()
            w._last_val = cur

    def perform_undo(event: tk.Event) -> str | None:
        w = getattr(event, "widget", None)
        if not isinstance(w, tk.Entry):
            return None
        undo_stack, redo_stack = get_stacks(w)
        if undo_stack:
            redo_stack.append(w._last_val)
            prev = undo_stack.pop()
            w.delete(0, tk.END)
            w.insert(0, prev)
            w._last_val = prev
        return "break"

    def perform_redo(event: tk.Event) -> str | None:
        w = getattr(event, "widget", None)
        if not isinstance(w, tk.Entry):
            return None
        undo_stack, redo_stack = get_stacks(w)
        if redo_stack:
            undo_stack.append(w._last_val)
            nxt = redo_stack.pop()
            w.delete(0, tk.END)
            w.insert(0, nxt)
            w._last_val = nxt
        return "break"

    def global_hotkey_handler(event: tk.Event) -> str | None:
        if not isinstance(getattr(event, "widget", None), tk.Entry):
            return None
        keycode = getattr(event, "keycode", 0)
        keysym = getattr(event, "keysym", "").lower()
        if keycode == 90 or keysym in ("z", "я"):
            return perform_undo(event)
        if keycode == 89 or keysym in ("y", "н"):
            return perform_redo(event)
        return None

    root.bind_all("<KeyRelease>", track_changes, add="+")
    root.bind_all("<Control-KeyPress>", global_hotkey_handler, add="+")

def show_toast(master: tk.Widget, message: str, type: str = "success") -> None:
    if type == "success": bg_color = "#10B981"
    elif type == "error": bg_color = "#EF4444"
    elif type == "info": bg_color = "#3B82F6"
    else: bg_color = "#374151"
    
    toplevel = master.winfo_toplevel()
    toast = ctk.CTkFrame(toplevel, fg_color=bg_color, corner_radius=8)
    lbl = ctk.CTkLabel(toast, text=message, font=(FONT_FAMILY, 13, "bold"), text_color="#FFFFFF")
    lbl.pack(padx=24, pady=12)
    
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
        
        if hasattr(self.entry, "_entry"):
            self.entry._entry.bind("<KeyRelease>", self._on_key_release)
            self.entry._entry.bind("<FocusOut>", self._on_focus_out)
            self.entry._entry.bind("<FocusIn>", self._on_key_release)
            self.entry._entry.bind("<Down>", self._on_arrow_down)

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
            self.popup.configure(bg="#D1D5DB")
            
            frame = tk.Frame(self.popup, bg="white")
            frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
            
            scrollbar = tk.Scrollbar(frame, orient="vertical")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.listbox = tk.Listbox(
                frame, 
                font=("Segoe UI", 11), 
                bg="white", 
                fg="#111827", 
                selectbackground="#4F46E5", 
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
