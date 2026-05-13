import tkinter as tk
import customtkinter as ctk
from app.ui import BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT, CORNER_RADIUS, FlatButton, FONT_FAMILY

class DeleteGroupDialog(ctk.CTkToplevel):
    def __init__(self, master, group_name: str, student_count: int, on_confirm: callable):
        super().__init__(master)
        self.title("Удаление группы")
        self.geometry("440x320")
        self.resizable(False, False)
        self.configure(fg_color=BG_CARD)
        self.transient(master)
        self.grab_set()
        
        self.on_confirm = on_confirm

        # Center on screen
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (440 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (320 // 2)
        self.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self, 
            text="⚠️ Внимание!", 
            font=(FONT_FAMILY, 20, "bold"),
            text_color="#dc2626"
        )
        label.pack(pady=(24, 12))

        msg = f"В группе '{group_name}' сейчас {student_count} чел.\nПри удалении группы все студенты будут удалены безвозвратно!"
        desc = ctk.CTkLabel(
            self, 
            text=msg, 
            font=(FONT_FAMILY, 14),
            text_color=TEXT_COLOR,
            wraplength=380,
            justify="center"
        )
        desc.pack(padx=30, pady=10)

        self.confirm_var = tk.BooleanVar(value=False)
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="Я подтверждаю удаление группы и всех студентов",
            variable=self.confirm_var,
            font=(FONT_FAMILY, 12),
            text_color=TEXT_MUTED,
            fg_color=ACCENT,
            hover_color=ACCENT,
            corner_radius=4,
            command=self._on_check
        )
        self.checkbox.pack(pady=(20, 0), padx=30)

        # Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=24)

        self.delete_btn = FlatButton(
            btn_frame, 
            text="Удалить всё", 
            primary=True, 
            danger=True,
            command=self._do_delete,
            height=40,
            width=150
        )
        self.delete_btn.pack(side=tk.RIGHT)
        self.delete_btn.set_state("disabled")

        cancel_btn = FlatButton(
            btn_frame, 
            text="Отмена", 
            primary=False, 
            command=self.destroy,
            height=40,
            width=100
        )
        cancel_btn.pack(side=tk.RIGHT, padx=12)

    def _on_check(self):
        if self.confirm_var.get():
            self.delete_btn.set_state("normal")
        else:
            self.delete_btn.set_state("disabled")

    def _do_delete(self):
        self.on_confirm()
        self.destroy()
