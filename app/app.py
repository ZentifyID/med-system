import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

from app.database import (
    delete_employee, fetch_employee_by_id, fetch_employees_for_table, init_db, insert_employee, update_employee,
    fetch_students_for_table, fetch_student_by_id, insert_student, update_student, delete_student,
    fetch_groups, fetch_group_by_id, insert_group, update_group, delete_group,
    fetch_medicines_for_table, fetch_medicine_by_id, insert_medicine, update_medicine, delete_medicine,
    fetch_appeals_for_table, fetch_appeal_by_id, insert_appeal, update_appeal, delete_appeal,
    fetch_all_person_names,
)
from app.pages.employee_form_page import EmployeeFormPage
from app.pages.employee_view_page import EmployeeViewPage
from app.pages.employees_page import EmployeesPage
from app.pages.students_page import StudentsPage
from app.pages.student_form_page import StudentFormPage
from app.pages.student_view_page import StudentViewPage
from app.pages.groups_page import GroupsPage
from app.pages.group_form_page import GroupFormPage
from app.pages.group_view_page import GroupViewPage
from app.pages.medicines_page import MedicinesPage
from app.pages.medicine_form_page import MedicineFormPage
from app.pages.medicine_view_page import MedicineViewPage
from app.pages.order_medicines_dialog import OrderMedicinesDialog
from app.pages.appeals_page import AppealsPage
from app.pages.appeal_form_page import AppealFormPage
from app.pages.appeal_view_page import AppealViewPage
from app.pages.main_page import MainPage
from app.ui import (
    BG_SIDEBAR, BG_COLOR, TEXT_SIDEBAR, ACCENT, TEXT_COLOR,
    setup_styles, SidebarButton,
)
import tkinter.font as tkfont


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Med System")
        self.root.geometry("1140x700")
        self.root.minsize(900, 560)
        self.root.configure(bg=BG_SIDEBAR)
        setup_styles(root)

        self.search_query = ""
        self.filter_status = "Все сотрудники"
        self.search_query_students = ""
        self.filter_status_students = "Все студенты"
        self.search_query_medicines = ""
        self.filter_status_medicines = "Все лекарства"
        self.search_query_appeals = ""

        # ── Shell layout ──────────────────────────────────────────────
        shell = tk.Frame(root, bg=BG_SIDEBAR)
        shell.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(shell, bg=BG_SIDEBAR, width=210)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Content
        self.content = tk.Frame(shell, bg=BG_COLOR)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_pages()

        self.show_main_page()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> None:
        # Logo / title
        logo_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(20, 8))

        tk.Label(
            logo_frame,
            text="⚕",
            font=("Segoe UI", 22),
            bg=BG_SIDEBAR,
            fg=ACCENT,
        ).pack(side=tk.LEFT, padx=(16, 8))

        tk.Label(
            logo_frame,
            text="MedSystem",
            font=("Segoe UI", 13, "bold"),
            bg=BG_SIDEBAR,
            fg="#FFFFFF",
        ).pack(side=tk.LEFT)

        # Divider
        tk.Frame(self.sidebar, bg="#1F2937", height=1).pack(fill=tk.X, padx=12, pady=(8, 12))

        # Nav section label
        tk.Label(
            self.sidebar,
            text="НАВИГАЦИЯ",
            font=("Segoe UI", 8),
            bg=BG_SIDEBAR,
            fg="#4B5563",
        ).pack(anchor="w", padx=18, pady=(0, 6))

        # Nav buttons
        nav_items = [
            ("🏠", "Главная",     self.show_main_page),
            ("👤", "Сотрудники",  self.show_employees_page),
            ("🎓", "Студенты",    self.show_students_page),
            ("💊", "Лекарства",   self.show_medicines_page),
            ("📋", "Обращения",   self.show_appeals_page),
        ]

        self._sidebar_buttons: dict[str, SidebarButton] = {}
        for icon, label, cmd in nav_items:
            btn = SidebarButton(self.sidebar, text=label, icon=icon, command=lambda c=cmd, l=label: self._nav_click(c, l))
            btn.pack(fill=tk.X, padx=8, pady=2)
            self._sidebar_buttons[label] = btn

        # Bottom section
        tk.Frame(self.sidebar, bg="#1F2937", height=1).pack(fill=tk.X, padx=12, pady=(16, 8), side=tk.BOTTOM)
        tk.Label(
            self.sidebar,
            text="Med System v2.0",
            font=("Segoe UI", 8),
            bg=BG_SIDEBAR,
            fg="#374151",
        ).pack(side=tk.BOTTOM, pady=(0, 16))

    def _nav_click(self, command, label: str) -> None:
        for lbl, btn in self._sidebar_buttons.items():
            btn.set_active(lbl == label)
        command()

    def _set_active_nav(self, label: str) -> None:
        for lbl, btn in self._sidebar_buttons.items():
            btn.set_active(lbl == label)

    # ── Pages ─────────────────────────────────────────────────────────────────
    def _build_pages(self) -> None:
        c = self.content
        self.main_page = MainPage(c, on_employees=self.show_employees_page, on_students=self.show_students_page, on_medicines=self.show_medicines_page, on_appeals=self.show_appeals_page)
        self.employees_page = EmployeesPage(c, on_add=self.show_add_employee_page, on_back=self.show_main_page, on_select=self.show_employee_view_page, on_filter_changed=self.on_filter_changed)
        self.employee_form_page = EmployeeFormPage(c, on_save=self.save_employee, on_cancel=self.show_employees_page)
        self.employee_view_page = EmployeeViewPage(c, on_save=self.edit_employee, on_delete=self.delete_employee_action, on_cancel=self.show_employees_page)

        self.students_page = StudentsPage(c, on_add=self.show_add_student_page, on_groups=self.show_groups_page, on_back=self.show_main_page, on_select=self.show_student_view_page, on_filter_changed=self.on_filter_changed_students)
        self.student_form_page = StudentFormPage(c, on_save=self.save_student, on_cancel=self.show_students_page)
        self.student_view_page = StudentViewPage(c, on_save=self.edit_student, on_delete=self.delete_student_action, on_cancel=self.show_students_page)
        self.groups_page = GroupsPage(c, on_add=self.show_add_group_page, on_back=self.show_students_page, on_select=self.show_group_view_page)
        self.group_form_page = GroupFormPage(c, on_save=self.save_group, on_cancel=self.show_groups_page)
        self.group_view_page = GroupViewPage(c, on_save=self.edit_group, on_delete=self.delete_group_action, on_cancel=self.show_groups_page)

        self.medicines_page = MedicinesPage(c, on_add=self.show_add_medicine_page, on_back=self.show_main_page, on_select=self.show_medicine_view_page, on_order=self.order_medicines_action, on_filter_changed=self.on_filter_changed_medicines)
        self.medicine_form_page = MedicineFormPage(c, on_save=self.save_medicine, on_cancel=self.show_medicines_page)
        self.medicine_view_page = MedicineViewPage(c, on_save=self.edit_medicine, on_delete=self.delete_medicine_action, on_cancel=self.show_medicines_page)

        self.appeals_page = AppealsPage(c, on_add=self.show_add_appeal_page, on_back=self.show_main_page, on_select=self.show_appeal_view_page, on_filter_changed=self.on_filter_changed_appeals)
        self.appeal_form_page = AppealFormPage(c, on_save=self.save_appeal, on_cancel=self.show_appeals_page)
        self.appeal_view_page = AppealViewPage(c, on_save=self.edit_appeal, on_delete=self.delete_appeal_action, on_cancel=self.show_appeals_page)

        self._all_pages = [
            self.main_page, self.employees_page, self.employee_form_page, self.employee_view_page,
            self.students_page, self.student_form_page, self.student_view_page,
            self.groups_page, self.group_form_page, self.group_view_page,
            self.medicines_page, self.medicine_form_page, self.medicine_view_page,
            self.appeals_page, self.appeal_form_page, self.appeal_view_page,
        ]

    def _show_page(self, page: tk.Frame) -> None:
        for p in self._all_pages:
            p.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)

    # ── Navigation ────────────────────────────────────────────────────────────
    def show_main_page(self) -> None:
        self._set_active_nav("Главная")
        self.main_page.refresh_counts()
        self._show_page(self.main_page)

    def show_employees_page(self) -> None:
        self._set_active_nav("Сотрудники")
        self.refresh_employees_table()
        self._show_page(self.employees_page)

    def show_add_employee_page(self) -> None:
        self._set_active_nav("Сотрудники")
        self.employee_form_page.reset_form()
        self._show_page(self.employee_form_page)

    def show_employee_view_page(self, employee_id: int) -> None:
        self._set_active_nav("Сотрудники")
        data = fetch_employee_by_id(employee_id)
        if data:
            self.employee_view_page.set_employee_data(data)
            self._show_page(self.employee_view_page)
        else:
            messagebox.showerror("Ошибка", "Сотрудник не найден")

    def on_filter_changed(self, search_query: str, filter_status: str) -> None:
        self.search_query = search_query.strip().lower()
        self.filter_status = filter_status
        self.refresh_employees_table()

    def refresh_employees_table(self) -> None:
        rows = fetch_employees_for_table()
        now = datetime.now()
        fourteen_days = now + timedelta(days=14)
        filtered = []
        for id, fio, affiliation, san_date, med_date, flu_date in rows:
            if self.search_query and self.search_query not in fio.lower():
                continue
            if self.filter_status != "Все сотрудники":
                exp_dates = []
                for d_str in (san_date, med_date, flu_date):
                    try:
                        d = datetime.strptime(d_str, "%d.%m.%Y")
                        try:
                            exp = d.replace(year=d.year + 1)
                        except ValueError:
                            exp = d.replace(year=d.year + 1, month=2, day=28)
                        exp_dates.append(exp)
                    except ValueError:
                        pass
                is_expired = any(e < now for e in exp_dates)
                is_expiring = any(now <= e <= fourteen_days for e in exp_dates)
                if self.filter_status == "Просроченные" and not is_expired:
                    continue
                if self.filter_status == "Истекают (2 недели)" and not is_expiring:
                    continue
            filtered.append((id, fio, affiliation))
        self.employees_page.set_rows(filtered)

    def save_employee(self, data: dict) -> None:
        try:
            insert_employee(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_employees_page()

    def edit_employee(self, employee_id: int, data: dict) -> None:
        try:
            update_employee(employee_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_employee_view_page(employee_id)

    def delete_employee_action(self, employee_id: int) -> None:
        try:
            delete_employee(employee_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_employees_page()

    # ── Students ──────────────────────────────────────────────────────────────
    def show_students_page(self) -> None:
        self._set_active_nav("Студенты")
        self.refresh_students_table()
        self._show_page(self.students_page)

    def show_add_student_page(self) -> None:
        self._set_active_nav("Студенты")
        groups = fetch_groups()
        if not groups:
            messagebox.showwarning("Внимание", "Сначала добавьте хотя бы одну учебную группу."); return
        self.student_form_page.set_groups(groups)
        self.student_form_page.reset_form()
        self._show_page(self.student_form_page)

    def show_student_view_page(self, student_id: int) -> None:
        self._set_active_nav("Студенты")
        data = fetch_student_by_id(student_id)
        if data:
            self.student_view_page.set_groups(fetch_groups())
            self.student_view_page.set_student_data(data)
            self._show_page(self.student_view_page)
        else:
            messagebox.showerror("Ошибка", "Студент не найден")

    def on_filter_changed_students(self, search_query: str, filter_status: str) -> None:
        self.search_query_students = search_query.strip().lower()
        self.filter_status_students = filter_status
        self.refresh_students_table()

    def refresh_students_table(self) -> None:
        rows = fetch_students_for_table()
        now = datetime.now()
        fourteen_days = now + timedelta(days=14)
        filtered = []
        for id, fio, group_name, san_date, med_date, flu_date in rows:
            if self.search_query_students and self.search_query_students not in fio.lower():
                continue
            if self.filter_status_students != "Все студенты":
                exp_dates = []
                for d_str in (san_date, med_date, flu_date):
                    try:
                        d = datetime.strptime(d_str, "%d.%m.%Y")
                        try:
                            exp = d.replace(year=d.year + 1)
                        except ValueError:
                            exp = d.replace(year=d.year + 1, month=2, day=28)
                        exp_dates.append(exp)
                    except ValueError:
                        pass
                is_expired = any(e < now for e in exp_dates)
                is_expiring = any(now <= e <= fourteen_days for e in exp_dates)
                if self.filter_status_students == "Просроченные" and not is_expired:
                    continue
                if self.filter_status_students == "Истекают (2 недели)" and not is_expiring:
                    continue
            filtered.append((id, fio, group_name))
        self.students_page.set_rows(filtered)

    def save_student(self, data: dict) -> None:
        try:
            insert_student(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_students_page()

    def edit_student(self, student_id: int, data: dict) -> None:
        try:
            update_student(student_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_student_view_page(student_id)

    def delete_student_action(self, student_id: int) -> None:
        try:
            delete_student(student_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_students_page()

    # ── Groups ────────────────────────────────────────────────────────────────
    def show_groups_page(self) -> None:
        self._set_active_nav("Студенты")
        self.groups_page.set_rows(fetch_groups())
        self._show_page(self.groups_page)

    def show_add_group_page(self) -> None:
        self.group_form_page.reset_form()
        self._show_page(self.group_form_page)

    def show_group_view_page(self, group_id: int) -> None:
        data = fetch_group_by_id(group_id)
        if data:
            self.group_view_page.set_group_data(data)
            self._show_page(self.group_view_page)
        else:
            messagebox.showerror("Ошибка", "Группа не найдена")

    def save_group(self, name: str) -> None:
        try:
            insert_group(name)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует."); return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_groups_page()

    def edit_group(self, group_id: int, name: str) -> None:
        try:
            update_group(group_id, name)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует."); return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_group_view_page(group_id)

    def delete_group_action(self, group_id: int) -> None:
        try:
            delete_group(group_id)
        except sqlite3.IntegrityError:
            messagebox.showwarning("Ошибка удаления", "Невозможно удалить группу — в ней есть студенты."); return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_groups_page()

    # ── Medicines ─────────────────────────────────────────────────────────────
    def show_medicines_page(self) -> None:
        self._set_active_nav("Лекарства")
        self.refresh_medicines_table()
        self._show_page(self.medicines_page)

    def show_add_medicine_page(self) -> None:
        self._set_active_nav("Лекарства")
        self.medicine_form_page.reset_form()
        self._show_page(self.medicine_form_page)

    def show_medicine_view_page(self, medicine_id: int) -> None:
        self._set_active_nav("Лекарства")
        data = fetch_medicine_by_id(medicine_id)
        if data:
            self.medicine_view_page.set_medicine_data(data)
            self._show_page(self.medicine_view_page)
        else:
            messagebox.showerror("Ошибка", "Лекарство не найдено")

    def on_filter_changed_medicines(self, search_query: str, filter_status: str) -> None:
        self.search_query_medicines = search_query.strip().lower()
        self.filter_status_medicines = filter_status
        self.refresh_medicines_table()

    def refresh_medicines_table(self) -> None:
        rows = fetch_medicines_for_table()
        now = datetime.now()
        fourteen_days = now + timedelta(days=14)
        filtered = []
        for id, name, unit, qty, exp_date_str in rows:
            if self.search_query_medicines and self.search_query_medicines not in name.lower():
                continue
            is_expired = is_expiring = False
            if exp_date_str:
                try:
                    d = datetime.strptime(exp_date_str, "%d.%m.%Y")
                    is_expired = d < now
                    is_expiring = d <= fourteen_days
                except ValueError:
                    pass
            is_low_qty = qty <= 5
            if self.filter_status_medicines == "Просроченные" and not is_expired: continue
            if self.filter_status_medicines == "Истекают (2 недели)" and not is_expiring: continue
            if self.filter_status_medicines == "Мало (<= 5)" and not is_low_qty: continue
            filtered.append((id, name, qty, unit, exp_date_str, is_expiring, is_low_qty))
        self.medicines_page.set_rows(filtered)

    def save_medicine(self, data: dict) -> None:
        try:
            insert_medicine(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_medicines_page()

    def edit_medicine(self, medicine_id: int, data: dict) -> None:
        try:
            update_medicine(medicine_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_medicine_view_page(medicine_id)

    def delete_medicine_action(self, medicine_id: int) -> None:
        try:
            delete_medicine(medicine_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_medicines_page()

    def order_medicines_action(self) -> None:
        rows = fetch_medicines_for_table()
        now = datetime.now()
        fourteen_days = now + timedelta(days=14)
        to_order = []
        for id, name, unit, qty, exp_date_str in rows:
            is_expired = is_expiring = False
            if exp_date_str:
                try:
                    d = datetime.strptime(exp_date_str, "%d.%m.%Y")
                    is_expired = d < now
                    is_expiring = d <= fourteen_days
                except ValueError:
                    pass
            if qty <= 5 or is_expiring:
                to_order.append({"id": id, "name": name, "unit": unit, "quantity": qty, "expiration_date": exp_date_str})
        if not to_order:
            messagebox.showinfo("Заказ лекарств", "Все лекарства в норме. Заказывать ничего не нужно."); return
        OrderMedicinesDialog(self.root, to_order, self.confirm_order_medicines)

    def confirm_order_medicines(self, result: list) -> None:
        try:
            for item in result:
                delete_medicine(int(item["old_id"]))
                insert_medicine({"name": item["name"], "unit": item["unit"], "quantity": item["new_quantity"], "expiration_date": item["new_expiration_date"]})
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
        self.refresh_medicines_table()
        messagebox.showinfo("Успех", "Заказ оформлен: старые партии списаны, новые добавлены.")

    # ── Appeals ───────────────────────────────────────────────────────────────
    def show_appeals_page(self) -> None:
        self._set_active_nav("Обращения")
        self.refresh_appeals_table()
        self._show_page(self.appeals_page)

    def show_add_appeal_page(self) -> None:
        self._set_active_nav("Обращения")
        self.appeal_form_page.reset_form()
        self.appeal_form_page.set_senders(fetch_all_person_names())
        self._show_page(self.appeal_form_page)

    def show_appeal_view_page(self, appeal_id: int) -> None:
        self._set_active_nav("Обращения")
        data = fetch_appeal_by_id(appeal_id)
        if data:
            self.appeal_view_page.set_senders(fetch_all_person_names())
            self.appeal_view_page.set_appeal_data(data)
            self._show_page(self.appeal_view_page)
        else:
            messagebox.showerror("Ошибка", "Обращение не найдено")

    def on_filter_changed_appeals(self, search_query: str) -> None:
        self.search_query_appeals = search_query.strip().lower()
        self.refresh_appeals_table()

    def refresh_appeals_table(self) -> None:
        rows = fetch_appeals_for_table()
        filtered = []
        for id, title, sender, created_at in rows:
            if self.search_query_appeals and (self.search_query_appeals not in title.lower() and self.search_query_appeals not in sender.lower()):
                continue
            filtered.append((id, title, sender, created_at))
        self.appeals_page.set_rows(filtered)

    def save_appeal(self, data: dict) -> None:
        try:
            insert_appeal(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_appeals_page()

    def edit_appeal(self, appeal_id: int, data: dict) -> None:
        try:
            update_appeal(appeal_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_appeal_view_page(appeal_id)

    def delete_appeal_action(self, appeal_id: int) -> None:
        try:
            delete_appeal(appeal_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc)); return
        self.show_appeals_page()


def run_app() -> None:
    init_db()
    root = tk.Tk()
    App(root)
    root.mainloop()
