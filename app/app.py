import sqlite3
import tkinter as tk
from tkinter import messagebox

from app.database import fetch_employees_for_table, init_db, insert_employee
from app.pages.employee_form_page import EmployeeFormPage
from app.pages.employees_page import EmployeesPage
from app.pages.main_page import MainPage


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Med System")
        self.root.geometry("980x620")
        self.root.minsize(820, 520)
        self.root.configure(bg="#f3f4f6")

        self.main_page = MainPage(root, on_employees=self.show_employees_page)
        self.employees_page = EmployeesPage(
            root,
            on_add=self.show_add_employee_page,
            on_back=self.show_main_page,
        )
        self.employee_form_page = EmployeeFormPage(
            root,
            on_save=self.save_employee,
            on_cancel=self.show_employees_page,
        )
        self.show_main_page()

    def _show_page(self, page: tk.Frame) -> None:
        self.main_page.pack_forget()
        self.employees_page.pack_forget()
        self.employee_form_page.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)

    def show_main_page(self) -> None:
        self._show_page(self.main_page)

    def show_employees_page(self) -> None:
        self.refresh_employees_table()
        self._show_page(self.employees_page)

    def show_add_employee_page(self) -> None:
        self.employee_form_page.reset_form()
        self._show_page(self.employee_form_page)

    def refresh_employees_table(self) -> None:
        rows = fetch_employees_for_table()
        self.employees_page.set_rows(rows)

    def save_employee(self, data: dict[str, str]) -> None:
        try:
            insert_employee(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить сотрудника:\n{exc}")
            return

        self.show_employees_page()


def run_app() -> None:
    init_db()
    root = tk.Tk()
    App(root)
    root.mainloop()
