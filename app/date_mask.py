import tkinter as tk

import customtkinter as ctk


class DateMaskHandler:
    """Handles date input with the DD.MM.YYYY mask."""

    PLACEHOLDER = "__.__.____"

    @staticmethod
    def bind_to_entry(entry_widget: tk.Widget | ctk.CTkEntry, string_var: tk.StringVar) -> None:
        inner_entry = entry_widget._entry if hasattr(entry_widget, "_entry") else entry_widget
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
        if self.var.get() == self.PLACEHOLDER:
            self.var.set("")

    def on_focus_out(self, event: tk.Event) -> None:
        if not self.var.get().strip():
            self.var.set(self.PLACEHOLDER)

    def _fmt(self, digits: str) -> str:
        if len(digits) <= 2:
            return digits
        if len(digits) <= 4:
            return f"{digits[:2]}.{digits[2:]}"
        return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"

    def _d2i(self, display: str, idx: int) -> int:
        return sum(1 for char in display[:idx] if char.isdigit())

    def _i2d(self, index: int) -> int:
        if index <= 2:
            return index
        if index <= 4:
            return index + 1
        return index + 2

    def _digits(self, value: str) -> str:
        return "".join(char for char in value if char.isdigit())[:8]

    def _replace(self, digits: str, start: int, end: int, replacement: str = "") -> str:
        return (digits[:start] + replacement + digits[end:])[:8]

    def _apply(self, digits: str, caret: int) -> str:
        digits = digits[:8]
        self.var.set(self._fmt(digits))
        self.entry.icursor(self._i2d(max(0, min(caret, len(digits)))))
        return "break"

    def on_keypress(self, event: tk.Event) -> str | None:
        current_value = self.entry.get()
        if current_value == self.PLACEHOLDER:
            current_value = ""

        digits = self._digits(current_value)
        has_selection = self.entry.selection_present()
        if has_selection:
            start = self._d2i(current_value, self.entry.index("sel.first"))
            end = self._d2i(current_value, self.entry.index("sel.last"))
        else:
            start = end = self._d2i(current_value, self.entry.index(tk.INSERT))

        ctrl_pressed = bool(event.state & 0x4)
        if ctrl_pressed and event.keysym.lower() == "v":
            return self.on_paste(event)
        if ctrl_pressed:
            return None

        if event.keysym in {"Left", "Right", "Home", "End", "Tab", "ISO_Left_Tab", "Shift_L", "Shift_R"}:
            return None

        if event.keysym == "BackSpace":
            if has_selection:
                return self._apply(self._replace(digits, start, end), start)
            if start == 0:
                return "break"
            return self._apply(self._replace(digits, start - 1, start), start - 1)

        if event.keysym == "Delete":
            if has_selection:
                return self._apply(self._replace(digits, start, end), start)
            if start >= len(digits):
                return "break"
            return self._apply(self._replace(digits, start, start + 1), start)

        if event.char.isdigit():
            if len(digits) >= 8 and not has_selection:
                return "break"
            return self._apply(self._replace(digits, start, end, event.char), start + 1)

        return "break"

    def on_paste(self, event: tk.Event) -> str:
        current_value = self.entry.get()
        if current_value == self.PLACEHOLDER:
            current_value = ""

        digits = self._digits(current_value)
        try:
            clipboard_value = self.entry.clipboard_get()
        except tk.TclError:
            return "break"

        pasted_digits = "".join(char for char in clipboard_value if char.isdigit())
        if not pasted_digits:
            return "break"

        has_selection = self.entry.selection_present()
        if has_selection:
            start = self._d2i(current_value, self.entry.index("sel.first"))
            end = self._d2i(current_value, self.entry.index("sel.last"))
        else:
            start = end = self._d2i(current_value, self.entry.index(tk.INSERT))

        next_digits = self._replace(digits, start, end, pasted_digits)
        return self._apply(next_digits, min(start + len(pasted_digits), len(next_digits)))
