import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from app.ui import (
    BG_COLOR,
    ENTRY_BG,
    ENTRY_FG,
    TEXT_COLOR,
    TEXT_MUTED,
    FlatButton,
)
from app.validators import (
    DATE_FIELDS,
    STUDENT_FIELD_LABELS as FIELD_LABELS,
    allow_typed_value,
    validate_student_payload,
)

DATE_PLACEHOLDER = "__.__.____"


class StudentFormPage(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_save: Callable[[dict[str, str]], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(master, bg=BG_COLOR)
        self._on_save = on_save
        self._on_cancel = on_cancel
        self._validate_cmd = (self.register(self._validate_input), "%P", "%W")
        self.form_vars: dict[str, tk.StringVar] = {}
        self.form_entries: dict[str, tk.Widget] = {}
        self.group_mapping: dict[str, str] = {}
        self.group_combobox: ttk.Combobox | None = None

        title = tk.Label(
            self,
            text="Добавление студента",
            font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title.pack(pady=(30, 20))

        fields: list[tuple[str, str]] = [
            ("last_name", FIELD_LABELS["last_name"]),
            ("first_name", FIELD_LABELS["first_name"]),
            ("middle_name", FIELD_LABELS["middle_name"]),
            ("birth_date", FIELD_LABELS["birth_date"]),
            ("group_id", FIELD_LABELS["group_id"]),
            ("passport_series", FIELD_LABELS["passport_series"]),
            ("passport_number", FIELD_LABELS["passport_number"]),
            ("passport_issued_by", FIELD_LABELS["passport_issued_by"]),
            ("passport_issue_date", FIELD_LABELS["passport_issue_date"]),
            ("passport_department_code", FIELD_LABELS["passport_department_code"]),
            ("oms", FIELD_LABELS["oms"]),
            ("address", FIELD_LABELS["address"]),
            ("sanminimum_date", FIELD_LABELS["sanminimum_date"]),
            ("medical_exam_date", FIELD_LABELS["medical_exam_date"]),
            ("fluorography_date", FIELD_LABELS["fluorography_date"]),
        ]

        form_container = tk.Frame(self, bg=BG_COLOR)
        form_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        for i in range(2):
            form_container.grid_columnconfigure(i * 2, weight=0)
            form_container.grid_columnconfigure(i * 2 + 1, weight=1)

        left_count = (len(fields) + 1) // 2
        for idx, (key, label) in enumerate(fields):
            block = 0 if idx < left_count else 1
            row = idx if idx < left_count else idx - left_count
            label_col = block * 2
            input_col = label_col + 1

            tk.Label(
                form_container,
                text=label,
                font=("Segoe UI", 10),
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                anchor="w",
            ).grid(row=row, column=label_col, sticky="w", padx=(0, 12), pady=8)

            var = tk.StringVar()
            self.form_vars[key] = var

            if key == "group_id":
                field = ttk.Combobox(
                    form_container,
                    textvariable=var,
                    state="readonly",
                )
                self.group_combobox = field
                self.form_entries[key] = field
            else:
                field = tk.Entry(
                    form_container,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    validate="key",
                    validatecommand=self._validate_cmd,
                    name=f"field_{key}",
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    relief=tk.SOLID,
                    borderwidth=1,
                )
                self.form_entries[key] = field
                if key in DATE_FIELDS:
                    field.bind("<FocusIn>", lambda _event, k=key: self._on_date_focus_in(k))
                    field.bind("<FocusOut>", lambda _event, k=key: self._on_date_focus_out(k))
                    field.bind("<KeyPress>", lambda event, k=key: self._on_date_keypress(event, k))
                    field.bind("<Control-v>", lambda event, k=key: self._on_date_paste(event, k))
                    field.bind("<<Paste>>", lambda event, k=key: self._on_date_paste(event, k))
            field.grid(row=row, column=input_col, sticky="ew", padx=(0, 24), pady=8)

        hint = tk.Label(
            self,
            text="Формат дат: ДД.ММ.ГГГГ",
            font=("Segoe UI", 9, "italic"),
            bg=BG_COLOR,
            fg=TEXT_MUTED,
        )
        hint.pack(anchor="w", padx=32, pady=(0, 10))

        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(fill=tk.X, padx=30, pady=(10, 30))

        save_button = FlatButton(
            actions,
            primary=True,
            text="Сохранить",
            width=14,
            command=self._submit,
        )
        save_button.pack(side=tk.LEFT)

        cancel_button = FlatButton(
            actions,
            primary=False,
            text="Отмена",
            width=14,
            command=self._on_cancel,
        )
        cancel_button.pack(side=tk.LEFT, padx=(12, 0))

    def set_groups(self, groups: list[tuple[int, str]]) -> None:
        self.group_mapping = {name: str(id) for id, name in groups}
        if self.group_combobox:
            self.group_combobox["values"] = list(self.group_mapping.keys())
            if self.group_mapping:
                self.group_combobox.current(0)
            else:
                self.form_vars["group_id"].set("")

    def reset_form(self) -> None:
        for key, var in self.form_vars.items():
            if key == "group_id":
                if self.group_combobox and self.group_mapping:
                    self.group_combobox.current(0)
                else:
                    var.set("")
            elif key in DATE_FIELDS:
                var.set(DATE_PLACEHOLDER)
            else:
                var.set("")

    def _validate_input(self, proposed_value: str, widget_path: str) -> bool:
        field_name = widget_path.split(".")[-1].replace("field_", "")
        if field_name not in self.form_vars:
            return True
        return allow_typed_value(field_name, proposed_value)

    def _submit(self) -> None:
        data = {key: var.get().strip() for key, var in self.form_vars.items()}
        for date_field in DATE_FIELDS:
            if data[date_field] == DATE_PLACEHOLDER:
                data[date_field] = ""
        
        group_name = data["group_id"]
        data["group_id"] = self.group_mapping.get(group_name, "")

        errors = validate_student_payload(data)
        if errors:
            messagebox.showwarning("Ошибка ввода", "\n".join(errors[:5]))
            return

        self._on_save(data)

    def _on_date_focus_in(self, field_name: str) -> None:
        if self.form_vars[field_name].get() == DATE_PLACEHOLDER:
            self.form_vars[field_name].set("")

    def _on_date_focus_out(self, field_name: str) -> None:
        if not self.form_vars[field_name].get().strip():
            self.form_vars[field_name].set(DATE_PLACEHOLDER)

    def _format_date_digits(self, digits: str) -> str:
        if len(digits) <= 2:
            return digits
        if len(digits) <= 4:
            return f"{digits[:2]}.{digits[2:]}"
        return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"

    def _display_to_digit_index(self, display_value: str, display_index: int) -> int:
        return sum(1 for char in display_value[:display_index] if char.isdigit())

    def _digit_to_display_index(self, digit_index: int) -> int:
        if digit_index <= 2:
            return digit_index
        if digit_index <= 4:
            return digit_index + 1
        return digit_index + 2

    def _extract_digits(self, value: str) -> str:
        return "".join(char for char in value if char.isdigit())[:8]

    def _replace_digits_range(
        self,
        digits: str,
        start_digit: int,
        end_digit: int,
        replacement: str = "",
    ) -> str:
        return (digits[:start_digit] + replacement + digits[end_digit:])[:8]

    def _apply_date_digits(self, field_name: str, digits: str, caret_digit_index: int) -> str:
        digits = digits[:8]
        formatted = self._format_date_digits(digits)
        self.form_vars[field_name].set(formatted)

        entry = self.form_entries[field_name]
        safe_digit_index = max(0, min(caret_digit_index, len(digits)))
        entry.icursor(self._digit_to_display_index(safe_digit_index)) # type: ignore
        return "break"

    def _on_date_keypress(self, event: tk.Event, field_name: str) -> str | None:
        entry = self.form_entries[field_name]
        current_value = entry.get()
        if current_value == DATE_PLACEHOLDER:
            current_value = ""

        digits = self._extract_digits(current_value)
        selection_exists = entry.selection_present() # type: ignore
        if selection_exists:
            sel_start = entry.index("sel.first") # type: ignore
            sel_end = entry.index("sel.last") # type: ignore
            start_digit = self._display_to_digit_index(current_value, sel_start)
            end_digit = self._display_to_digit_index(current_value, sel_end)
        else:
            caret_display = entry.index(tk.INSERT) # type: ignore
            start_digit = self._display_to_digit_index(current_value, caret_display)
            end_digit = start_digit

        is_ctrl_pressed = bool(event.state & 0x4)
        if is_ctrl_pressed and event.keysym.lower() in {"a", "c", "x"}:
            return None
        if is_ctrl_pressed and event.keysym.lower() == "v":
            return self._on_date_paste(event, field_name)

        if event.keysym in {"Left", "Right", "Home", "End", "Tab", "ISO_Left_Tab", "Shift_L", "Shift_R"}:
            return None

        if event.keysym == "BackSpace":
            if selection_exists:
                new_digits = self._replace_digits_range(digits, start_digit, end_digit)
                return self._apply_date_digits(field_name, new_digits, start_digit)
            if start_digit == 0:
                return "break"
            new_digits = self._replace_digits_range(digits, start_digit - 1, start_digit)
            return self._apply_date_digits(field_name, new_digits, start_digit - 1)

        if event.keysym == "Delete":
            if selection_exists:
                new_digits = self._replace_digits_range(digits, start_digit, end_digit)
                return self._apply_date_digits(field_name, new_digits, start_digit)
            if start_digit >= len(digits):
                return "break"
            new_digits = self._replace_digits_range(digits, start_digit, start_digit + 1)
            return self._apply_date_digits(field_name, new_digits, start_digit)

        if event.char.isdigit():
            if len(digits) >= 8 and not selection_exists:
                return "break"
            new_digits = self._replace_digits_range(digits, start_digit, end_digit, event.char)
            return self._apply_date_digits(field_name, new_digits, start_digit + 1)

        return "break"

    def _on_date_paste(self, _event: tk.Event, field_name: str) -> str:
        entry = self.form_entries[field_name]
        current_value = entry.get()
        if current_value == DATE_PLACEHOLDER:
            current_value = ""

        digits = self._extract_digits(current_value)

        try:
            clipboard = self.clipboard_get()
        except tk.TclError:
            return "break"

        pasted_digits = "".join(char for char in clipboard if char.isdigit())
        if not pasted_digits:
            return "break"

        selection_exists = entry.selection_present() # type: ignore
        if selection_exists:
            sel_start = entry.index("sel.first") # type: ignore
            sel_end = entry.index("sel.last") # type: ignore
            start_digit = self._display_to_digit_index(current_value, sel_start)
            end_digit = self._display_to_digit_index(current_value, sel_end)
        else:
            caret_display = entry.index(tk.INSERT) # type: ignore
            start_digit = self._display_to_digit_index(current_value, caret_display)
            end_digit = start_digit

        new_digits = self._replace_digits_range(digits, start_digit, end_digit, pasted_digits)
        caret_digit_index = min(start_digit + len(pasted_digits), len(new_digits))
        return self._apply_date_digits(field_name, new_digits, caret_digit_index)
