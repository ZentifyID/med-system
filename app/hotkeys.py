from collections import deque
import tkinter as tk


def setup_global_undo(root: tk.Tk) -> None:
    def get_stacks(widget: tk.Widget) -> tuple[deque, deque]:
        if not hasattr(widget, "_undo_stack"):
            widget._undo_stack = deque(maxlen=50)
            widget._redo_stack = deque(maxlen=50)
            widget._last_val = widget.get() if hasattr(widget, "get") else ""
        return widget._undo_stack, widget._redo_stack

    def track_changes(event: tk.Event) -> None:
        widget = getattr(event, "widget", None)
        if not isinstance(widget, tk.Entry):
            return

        keysym = getattr(event, "keysym", "")
        if keysym in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
            return

        state = getattr(event, "state", 0)
        if state & 0x0004 and keysym.lower() in ("z", "y"):
            return

        undo_stack, redo_stack = get_stacks(widget)
        try:
            current_value = widget.get()
        except Exception:
            return

        if current_value != widget._last_val:
            undo_stack.append(widget._last_val)
            redo_stack.clear()
            widget._last_val = current_value

    def perform_undo(event: tk.Event) -> str | None:
        widget = getattr(event, "widget", None)
        if isinstance(widget, tk.Text):
            try:
                widget.edit_undo()
            except tk.TclError:
                pass
            return "break"

        if not isinstance(widget, tk.Entry):
            return None

        undo_stack, redo_stack = get_stacks(widget)
        if undo_stack:
            redo_stack.append(widget._last_val)
            previous_value = undo_stack.pop()
            widget.delete(0, tk.END)
            widget.insert(0, previous_value)
            widget._last_val = previous_value
        return "break"

    def perform_redo(event: tk.Event) -> str | None:
        widget = getattr(event, "widget", None)
        if isinstance(widget, tk.Text):
            try:
                widget.edit_redo()
            except tk.TclError:
                pass
            return "break"

        if not isinstance(widget, tk.Entry):
            return None

        undo_stack, redo_stack = get_stacks(widget)
        if redo_stack:
            undo_stack.append(widget._last_val)
            next_value = redo_stack.pop()
            widget.delete(0, tk.END)
            widget.insert(0, next_value)
            widget._last_val = next_value
        return "break"

    def select_all(event: tk.Event) -> str | None:
        widget = getattr(event, "widget", None)
        if isinstance(widget, tk.Entry):
            widget.selection_range(0, tk.END)
            widget.icursor(tk.END)
            return "break"

        if isinstance(widget, tk.Text):
            widget.tag_add(tk.SEL, "1.0", "end-1c")
            widget.mark_set(tk.INSERT, "end-1c")
            widget.see(tk.INSERT)
            return "break"

        return None

    def global_hotkey_handler(event: tk.Event) -> str | None:
        if not isinstance(getattr(event, "widget", None), (tk.Entry, tk.Text)):
            return None

        keycode = getattr(event, "keycode", 0)
        keysym = getattr(event, "keysym", "").lower()
        if keycode == 65 or keysym == "a":
            return select_all(event)
        if keycode == 90 or keysym == "z":
            return perform_undo(event)
        if keycode == 89 or keysym == "y":
            return perform_redo(event)
        return None

    root.bind_all("<KeyRelease>", track_changes, add="+")
    root.bind_all("<Control-KeyPress>", global_hotkey_handler, add="+")
