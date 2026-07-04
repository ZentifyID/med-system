import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from app.ui import (
    BG_COLOR, BG_CARD, TEXT_COLOR, TEXT_MUTED, BORDER, ACCENT,
    CORNER_RADIUS, FlatButton, FONT_FAMILY, FONT_MEDIUM,
    ENTRY_BG, ENTRY_FG, ENTRY_BORDER
)
from app.pages.add_edit_icd_dialog import AddEditICDDialog


class ICDReferenceDialog(ctk.CTkToplevel):
    def __init__(self, master, fetch_cb, insert_cb, update_cb, delete_cb, search_icon=None):
        super().__init__(master)
        self.fetch_cb = fetch_cb
        self.insert_cb = insert_cb
        self.update_cb = update_cb
        self.delete_cb = delete_cb

        self.title("Справочник МКБ-10")
        self.geometry("640x540")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.transient(master)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (640 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (540 // 2)
        self.geometry(f"+{x}+{y}")

        # Title / Header
        hdr = tk.Frame(self, bg=BG_COLOR)
        hdr.pack(fill=tk.X, padx=24, pady=(20, 10))
        tk.Label(hdr, text="Справочник МКБ-10", font=(FONT_FAMILY, 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)

        # Search Bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._trigger_filter)

        search_bar = tk.Frame(self, bg=BG_COLOR)
        search_bar.pack(fill=tk.X, padx=24, pady=(0, 12))

        if search_icon:
            icon_label = ctk.CTkLabel(search_bar, text="", image=search_icon, width=24, height=24)
            icon_label.pack(side=tk.LEFT, padx=(0, 12))
        else:
            icon_label = ctk.CTkLabel(search_bar, text="🔍", font=(FONT_FAMILY, 16), text_color=TEXT_MUTED)
            icon_label.pack(side=tk.LEFT, padx=(0, 12))

        search_entry = ctk.CTkEntry(
            search_bar, textvariable=self.search_var,
            font=(FONT_FAMILY, 14), fg_color=BG_CARD, text_color=TEXT_COLOR,
            border_color=ENTRY_BORDER, corner_radius=CORNER_RADIUS,
            placeholder_text="Поиск по коду или диагнозу...", placeholder_text_color=TEXT_MUTED, height=36
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Actions Row - PACK FIRST DOCKED TO BOTTOM to guarantee visibility!
        actions = tk.Frame(self, bg=BG_COLOR)
        actions.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=(0, 20))

        FlatButton(actions, primary=True, text="Добавить", command=self._open_add, height=38, width=110).pack(side=tk.LEFT)
        FlatButton(actions, primary=False, text="Изменить", command=self._open_edit, height=38, width=110).pack(side=tk.LEFT, padx=10)
        FlatButton(actions, primary=False, danger=True, text="Удалить", command=self._delete, height=38, width=100).pack(side=tk.LEFT, padx=10)
        FlatButton(actions, primary=False, text="Закрыть", command=self.destroy, height=38, width=100).pack(side=tk.RIGHT)

        # Table Card Container - PACK SECOND to occupy all remaining space
        card = ctk.CTkFrame(self, fg_color=BG_CARD, border_color=BORDER, border_width=1, corner_radius=12)
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.table = ttk.Treeview(inner, columns=("code", "name"), show="headings")
        self.table.heading("code", text="Код", command=lambda: self._sort_column("code", False))
        self.table.heading("name", text="Наименование диагноза", command=lambda: self._sort_column("name", False))

        self.table.column("code", width=120, anchor=tk.CENTER, stretch=False)
        self.table.column("name", width=460, anchor=tk.W, stretch=True)

        self.table.tag_configure("odd", background=BG_CARD)
        self.table.tag_configure("even", background="#F5F5F6")

        sb = ctk.CTkScrollbar(
            inner, orientation="vertical", command=self.table.yview,
            fg_color="transparent", button_color="#C9C9CC",
            button_hover_color="#A9A9AD", width=14,
        )
        self.table.configure(yscrollcommand=sb.set)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))

        self.table.bind("<Double-1>", lambda e: self._open_edit())

        # Initial Load
        self._load_data()

    def _load_data(self):
        for item in self.table.get_children():
            self.table.delete(item)

        q = self.search_var.get().strip()
        rows = self.fetch_cb(q)

        for i, item in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            self.table.insert("", tk.END, iid=item["code"], values=(item["code"], item["name"]), tags=(tag,))

    def _trigger_filter(self, *args):
        self._load_data()

    def _open_add(self):
        AddEditICDDialog(self, on_save=self._on_insert_confirm)

    def _on_insert_confirm(self, code, name):
        success = self.insert_cb(code, name)
        if success:
            self._load_data()
        return success

    def _open_edit(self, event=None):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите запись из таблицы для редактирования.")
            return
        
        old_code = sel[0]
        vals = self.table.item(old_code, "values")
        if vals:
            AddEditICDDialog(self, on_save=self._on_update_confirm, old_code=old_code, old_name=vals[1])

    def _on_update_confirm(self, old_code, new_code, new_name):
        success = self.update_cb(old_code, new_code, new_name)
        if success:
            self._load_data()
        return success

    def _delete(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите запись из таблицы для удаления.")
            return

        code = sel[0]
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить код МКБ-10 '{code}'?"):
            self.delete_cb(code)
            self._load_data()

    def _sort_column(self, col, reverse):
        data = [(self.table.set(child, col), child) for child in self.table.get_children("")]
        data.sort(reverse=reverse)
        for index, (_, child) in enumerate(data):
            self.table.move(child, "", index)
            tag = "odd" if index % 2 == 0 else "even"
            self.table.item(child, tags=(tag,))
        self.table.heading(col, command=lambda: self._sort_column(col, not reverse))
