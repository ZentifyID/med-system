import sys
import tkinter

import customtkinter as ctk


_PATCH_APPLIED = False


def apply_combobox_patch() -> None:
    global _PATCH_APPLIED
    if _PATCH_APPLIED:
        return

    original_init = ctk.CTkComboBox.__init__
    original_draw = ctk.CTkComboBox._draw

    def patched_on_enter(self, event=0):
        if self._hover is True and self._state in (tkinter.NORMAL, "readonly") and len(self._values) > 0:
            if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="pointinghand")
            elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="hand2")

            self._canvas.itemconfig(
                "inner_parts_right",
                outline=self._apply_appearance_mode(self._fg_color),
                fill=self._apply_appearance_mode(self._fg_color),
            )
            self._canvas.itemconfig(
                "border_parts_right",
                outline=self._apply_appearance_mode(self._border_color),
                fill=self._apply_appearance_mode(self._border_color),
            )

    def patched_on_leave(self, event=0):
        if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")
        elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")

        self._canvas.itemconfig(
            "inner_parts_right",
            outline=self._apply_appearance_mode(self._fg_color),
            fill=self._apply_appearance_mode(self._fg_color),
        )
        self._canvas.itemconfig(
            "border_parts_right",
            outline=self._apply_appearance_mode(self._border_color),
            fill=self._apply_appearance_mode(self._border_color),
        )

    def open_combobox_from_field(combo: ctk.CTkComboBox) -> str:
        if getattr(combo, "_state", None) in (tkinter.NORMAL, "readonly") and len(getattr(combo, "_values", [])) > 0:
            combo.focus_set()
            combo._open_dropdown_menu()
        return "break"

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.configure(button_color=self._fg_color, button_hover_color=self._fg_color)
        if hasattr(self, "_entry"):
            self._entry.bind("<Button-1>", lambda _event, combo=self: open_combobox_from_field(combo), add="+")
            self._entry.configure(cursor="hand2")

    def patched_draw(self, no_color_updates=False):
        original_draw(self, no_color_updates)
        self._canvas.itemconfig(
            "inner_parts_right",
            outline=self._apply_appearance_mode(self._fg_color),
            fill=self._apply_appearance_mode(self._fg_color),
        )
        self._canvas.itemconfig(
            "border_parts_right",
            outline=self._apply_appearance_mode(self._border_color),
            fill=self._apply_appearance_mode(self._border_color),
        )
        self._canvas.itemconfig("dropdown_arrow", fill=self._apply_appearance_mode(self._text_color))

    ctk.CTkComboBox._on_enter = patched_on_enter
    ctk.CTkComboBox._on_leave = patched_on_leave
    ctk.CTkComboBox.__init__ = patched_init
    ctk.CTkComboBox._draw = patched_draw

    _PATCH_APPLIED = True
