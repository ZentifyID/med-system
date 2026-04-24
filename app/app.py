import sqlite3
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

from app.database import (
    delete_employee,
    fetch_employee_by_id,
    fetch_employees_for_table,
    init_db,
    insert_employee,
    update_employee,
    fetch_students_for_table,
    fetch_student_by_id,
    insert_student,
    update_student,
    delete_student,
    fetch_groups,
    fetch_group_by_id,
    insert_group,
    update_group,
    delete_group,
    fetch_medicines_for_table,
    fetch_medicine_by_id,
    insert_medicine,
    update_medicine,
    delete_medicine,
    fetch_appeals_for_table,
    fetch_appeal_by_id,
    insert_appeal,
    update_appeal,
    delete_appeal,
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
from app.ui import BG_COLOR, setup_styles


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Med System")
        self.root.geometry("980x620")
        self.root.minsize(820, 520)
        self.root.configure(bg=BG_COLOR)
        
        setup_styles(root)

        self.search_query = ""
        self.filter_status = "Все сотрудники"

        self.search_query_students = ""
        self.filter_status_students = "Все студенты"

        self.search_query_medicines = ""
        self.filter_status_medicines = "Все лекарства"
        
        self.search_query_appeals = ""

        self.main_page = MainPage(
            root, 
            on_employees=self.show_employees_page,
            on_students=self.show_students_page,
            on_medicines=self.show_medicines_page,
            on_appeals=self.show_appeals_page,
        )
        self.employees_page = EmployeesPage(
            root,
            on_add=self.show_add_employee_page,
            on_back=self.show_main_page,
            on_select=self.show_employee_view_page,
            on_filter_changed=self.on_filter_changed,
        )
        self.employee_form_page = EmployeeFormPage(
            root,
            on_save=self.save_employee,
            on_cancel=self.show_employees_page,
        )
        self.employee_view_page = EmployeeViewPage(
            root,
            on_save=self.edit_employee,
            on_delete=self.delete_employee_action,
            on_cancel=self.show_employees_page,
        )

        self.students_page = StudentsPage(
            root,
            on_add=self.show_add_student_page,
            on_groups=self.show_groups_page,
            on_back=self.show_main_page,
            on_select=self.show_student_view_page,
            on_filter_changed=self.on_filter_changed_students,
        )
        self.student_form_page = StudentFormPage(
            root,
            on_save=self.save_student,
            on_cancel=self.show_students_page,
        )
        self.student_view_page = StudentViewPage(
            root,
            on_save=self.edit_student,
            on_delete=self.delete_student_action,
            on_cancel=self.show_students_page,
        )
        self.groups_page = GroupsPage(
            root,
            on_add=self.show_add_group_page,
            on_back=self.show_students_page,
            on_select=self.show_group_view_page,
        )
        self.group_form_page = GroupFormPage(
            root,
            on_save=self.save_group,
            on_cancel=self.show_groups_page,
        )
        self.group_view_page = GroupViewPage(
            root,
            on_save=self.edit_group,
            on_delete=self.delete_group_action,
            on_cancel=self.show_groups_page,
        )

        self.medicines_page = MedicinesPage(
            root,
            on_add=self.show_add_medicine_page,
            on_back=self.show_main_page,
            on_select=self.show_medicine_view_page,
            on_order=self.order_medicines_action,
            on_filter_changed=self.on_filter_changed_medicines,
        )
        self.medicine_form_page = MedicineFormPage(
            root,
            on_save=self.save_medicine,
            on_cancel=self.show_medicines_page,
        )
        self.medicine_view_page = MedicineViewPage(
            root,
            on_save=self.edit_medicine,
            on_delete=self.delete_medicine_action,
            on_cancel=self.show_medicines_page,
        )

        self.appeals_page = AppealsPage(
            root,
            on_add=self.show_add_appeal_page,
            on_back=self.show_main_page,
            on_select=self.show_appeal_view_page,
            on_filter_changed=self.on_filter_changed_appeals,
        )
        self.appeal_form_page = AppealFormPage(
            root,
            on_save=self.save_appeal,
            on_cancel=self.show_appeals_page,
        )
        self.appeal_view_page = AppealViewPage(
            root,
            on_save=self.edit_appeal,
            on_delete=self.delete_appeal_action,
            on_cancel=self.show_appeals_page,
        )

        self.show_main_page()

    def _show_page(self, page: tk.Frame) -> None:
        self.main_page.pack_forget()
        self.employees_page.pack_forget()
        self.employee_form_page.pack_forget()
        self.employee_view_page.pack_forget()
        self.students_page.pack_forget()
        self.student_form_page.pack_forget()
        self.student_view_page.pack_forget()
        self.groups_page.pack_forget()
        self.group_form_page.pack_forget()
        self.group_view_page.pack_forget()
        self.medicines_page.pack_forget()
        self.medicine_form_page.pack_forget()
        self.medicine_view_page.pack_forget()
        self.appeals_page.pack_forget()
        self.appeal_form_page.pack_forget()
        self.appeal_view_page.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)

    def show_main_page(self) -> None:
        self._show_page(self.main_page)

    def show_employees_page(self) -> None:
        self.refresh_employees_table()
        self._show_page(self.employees_page)

    def show_add_employee_page(self) -> None:
        self.employee_form_page.reset_form()
        self._show_page(self.employee_form_page)

    def show_employee_view_page(self, employee_id: int) -> None:
        employee_data = fetch_employee_by_id(employee_id)
        if employee_data:
            self.employee_view_page.set_employee_data(employee_data)
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

        filtered_rows = []
        for id, fio, affiliation, san_date, med_date, flu_date in rows:
            if self.search_query and self.search_query not in fio.lower():
                continue

            if self.filter_status != "Все сотрудники":
                expiration_dates = []
                for d_str in (san_date, med_date, flu_date):
                    try:
                        d = datetime.strptime(d_str, "%d.%m.%Y")
                        try:
                            exp_date = d.replace(year=d.year + 1)
                        except ValueError:
                            # Handle Feb 29 on leap years
                            exp_date = d.replace(year=d.year + 1, month=2, day=28)
                        expiration_dates.append(exp_date)
                    except ValueError:
                        pass
                
                is_expired = any(exp_date < now for exp_date in expiration_dates)
                is_expiring = any(now <= exp_date <= fourteen_days for exp_date in expiration_dates)

                if self.filter_status == "Просроченные" and not is_expired:
                    continue
                if self.filter_status == "Истекают (2 недели)" and not is_expiring:
                    continue

            filtered_rows.append((id, fio, affiliation))
            
        self.employees_page.set_rows(filtered_rows)

    def save_employee(self, data: dict[str, str]) -> None:
        try:
            insert_employee(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить сотрудника:\n{exc}")
            return

        self.show_employees_page()

    def edit_employee(self, employee_id: int, data: dict[str, str]) -> None:
        try:
            update_employee(employee_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось обновить данные сотрудника:\n{exc}")
            return

        self.show_employee_view_page(employee_id)

    def delete_employee_action(self, employee_id: int) -> None:
        try:
            delete_employee(employee_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось удалить сотрудника:\n{exc}")
            return

        self.show_employees_page()

    # === Студенты ===
    def show_students_page(self) -> None:
        self.refresh_students_table()
        self._show_page(self.students_page)

    def show_add_student_page(self) -> None:
        groups = fetch_groups()
        if not groups:
            messagebox.showwarning("Внимание", "Сначала необходимо добавить хотя бы одну учебную группу.")
            return
        self.student_form_page.set_groups(groups)
        self.student_form_page.reset_form()
        self._show_page(self.student_form_page)

    def show_student_view_page(self, student_id: int) -> None:
        student_data = fetch_student_by_id(student_id)
        if student_data:
            groups = fetch_groups()
            self.student_view_page.set_groups(groups)
            self.student_view_page.set_student_data(student_data)
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

        filtered_rows = []
        for id, fio, group_name, san_date, med_date, flu_date in rows:
            if self.search_query_students and self.search_query_students not in fio.lower():
                continue

            if self.filter_status_students != "Все студенты":
                expiration_dates = []
                for d_str in (san_date, med_date, flu_date):
                    try:
                        d = datetime.strptime(d_str, "%d.%m.%Y")
                        try:
                            exp_date = d.replace(year=d.year + 1)
                        except ValueError:
                            exp_date = d.replace(year=d.year + 1, month=2, day=28)
                        expiration_dates.append(exp_date)
                    except ValueError:
                        pass
                
                is_expired = any(exp_date < now for exp_date in expiration_dates)
                is_expiring = any(now <= exp_date <= fourteen_days for exp_date in expiration_dates)

                if self.filter_status_students == "Просроченные" and not is_expired:
                    continue
                if self.filter_status_students == "Истекают (2 недели)" and not is_expiring:
                    continue

            filtered_rows.append((id, fio, group_name))
            
        self.students_page.set_rows(filtered_rows)

    def save_student(self, data: dict[str, str]) -> None:
        try:
            insert_student(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить студента:\n{exc}")
            return
        self.show_students_page()

    def edit_student(self, student_id: int, data: dict[str, str]) -> None:
        try:
            update_student(student_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось обновить данные студента:\n{exc}")
            return
        self.show_student_view_page(student_id)

    def delete_student_action(self, student_id: int) -> None:
        try:
            delete_student(student_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось удалить студента:\n{exc}")
            return
        self.show_students_page()

    # === Группы ===
    def show_groups_page(self) -> None:
        rows = fetch_groups()
        self.groups_page.set_rows(rows)
        self._show_page(self.groups_page)

    def show_add_group_page(self) -> None:
        self.group_form_page.reset_form()
        self._show_page(self.group_form_page)

    def show_group_view_page(self, group_id: int) -> None:
        group_data = fetch_group_by_id(group_id)
        if group_data:
            self.group_view_page.set_group_data(group_data)
            self._show_page(self.group_view_page)
        else:
            messagebox.showerror("Ошибка", "Группа не найдена")

    def save_group(self, name: str) -> None:
        try:
            insert_group(name)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует.")
            return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить группу:\n{exc}")
            return
        self.show_groups_page()

    def edit_group(self, group_id: int, name: str) -> None:
        try:
            update_group(group_id, name)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует.")
            return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось обновить группу:\n{exc}")
            return
        self.show_group_view_page(group_id)

    def delete_group_action(self, group_id: int) -> None:
        try:
            delete_group(group_id)
        except sqlite3.IntegrityError:
            messagebox.showwarning("Ошибка удаления", "Невозможно удалить группу, так как в ней есть студенты.")
            return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось удалить группу:\n{exc}")
            return
        self.show_groups_page()

    # === Лекарства ===
    def show_medicines_page(self) -> None:
        self.refresh_medicines_table()
        self._show_page(self.medicines_page)

    def show_add_medicine_page(self) -> None:
        self.medicine_form_page.reset_form()
        self._show_page(self.medicine_form_page)

    def show_medicine_view_page(self, medicine_id: int) -> None:
        medicine_data = fetch_medicine_by_id(medicine_id)
        if medicine_data:
            self.medicine_view_page.set_medicine_data(medicine_data)
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

        filtered_rows = []
        for id, name, unit, qty, exp_date_str in rows:
            if self.search_query_medicines and self.search_query_medicines not in name.lower():
                continue

            is_expired = False
            is_expiring = False
            if exp_date_str:
                try:
                    d = datetime.strptime(exp_date_str, "%d.%m.%Y")
                    is_expired = d < now
                    is_expiring = d <= fourteen_days
                except ValueError:
                    pass

            is_low_qty = qty <= 5

            if self.filter_status_medicines == "Просроченные" and not is_expired:
                continue
            if self.filter_status_medicines == "Истекают (2 недели)" and not is_expiring:
                continue
            if self.filter_status_medicines == "Мало (<= 5)" and not is_low_qty:
                continue

            filtered_rows.append((id, name, qty, unit, exp_date_str, is_expiring, is_low_qty))
            
        self.medicines_page.set_rows(filtered_rows)

    def save_medicine(self, data: dict[str, str]) -> None:
        try:
            insert_medicine(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить лекарство:\n{exc}")
            return
        self.show_medicines_page()

    def edit_medicine(self, medicine_id: int, data: dict[str, str]) -> None:
        try:
            update_medicine(medicine_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось обновить лекарство:\n{exc}")
            return
        self.show_medicine_view_page(medicine_id)

    def delete_medicine_action(self, medicine_id: int) -> None:
        try:
            delete_medicine(medicine_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось удалить лекарство:\n{exc}")
            return
        self.show_medicines_page()

    def order_medicines_action(self) -> None:
        rows = fetch_medicines_for_table()
        now = datetime.now()
        fourteen_days = now + timedelta(days=14)
        
        to_order = []
        for id, name, unit, qty, exp_date_str in rows:
            is_expired = False
            is_expiring = False
            if exp_date_str:
                try:
                    d = datetime.strptime(exp_date_str, "%d.%m.%Y")
                    is_expired = d < now
                    is_expiring = d <= fourteen_days
                except ValueError:
                    pass
            
            is_low_qty = qty <= 5
            
            if is_low_qty or is_expiring:
                to_order.append({
                    "id": id,
                    "name": name,
                    "unit": unit,
                    "quantity": qty,
                    "expiration_date": exp_date_str
                })
                
        if not to_order:
            messagebox.showinfo("Заказ лекарств", "Все лекарства в достаточном количестве и с нормальным сроком годности. Заказывать ничего не нужно.")
            return
            
        OrderMedicinesDialog(self.root, to_order, self.confirm_order_medicines)
        
    def confirm_order_medicines(self, result_to_order: list[dict[str, str]]) -> None:
        try:
            for item in result_to_order:
                old_id = int(item["old_id"])
                delete_medicine(old_id)
                
                new_data = {
                    "name": item["name"],
                    "unit": item["unit"],
                    "quantity": item["new_quantity"],
                    "expiration_date": item["new_expiration_date"]
                }
                insert_medicine(new_data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Произошла ошибка при оформлении заказа:\n{exc}")
            
        self.refresh_medicines_table()
        messagebox.showinfo("Успех", "Заказ оформлен: старые партии списаны, новые добавлены.")

    # === Обращения ===
    def show_appeals_page(self) -> None:
        self.refresh_appeals_table()
        self._show_page(self.appeals_page)

    def show_add_appeal_page(self) -> None:
        self.appeal_form_page.reset_form()
        senders = fetch_all_person_names()
        self.appeal_form_page.set_senders(senders)
        self._show_page(self.appeal_form_page)

    def show_appeal_view_page(self, appeal_id: int) -> None:
        appeal_data = fetch_appeal_by_id(appeal_id)
        if appeal_data:
            senders = fetch_all_person_names()
            self.appeal_view_page.set_senders(senders)
            self.appeal_view_page.set_appeal_data(appeal_data)
            self._show_page(self.appeal_view_page)
        else:
            messagebox.showerror("Ошибка", "Обращение не найдено")

    def on_filter_changed_appeals(self, search_query: str) -> None:
        self.search_query_appeals = search_query.strip().lower()
        self.refresh_appeals_table()

    def refresh_appeals_table(self) -> None:
        rows = fetch_appeals_for_table()
        
        filtered_rows = []
        for id, title, sender, created_at in rows:
            if self.search_query_appeals and (self.search_query_appeals not in title.lower() and self.search_query_appeals not in sender.lower()):
                continue
            filtered_rows.append((id, title, sender, created_at))
            
        self.appeals_page.set_rows(filtered_rows)

    def save_appeal(self, data: dict[str, str]) -> None:
        try:
            insert_appeal(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить обращение:\n{exc}")
            return
        self.show_appeals_page()

    def edit_appeal(self, appeal_id: int, data: dict[str, str]) -> None:
        try:
            update_appeal(appeal_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось обновить обращение:\n{exc}")
            return
        self.show_appeal_view_page(appeal_id)

    def delete_appeal_action(self, appeal_id: int) -> None:
        try:
            delete_appeal(appeal_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", f"Не удалось удалить обращение:\n{exc}")
            return
        self.show_appeals_page()


def run_app() -> None:
    init_db()
    root = tk.Tk()
    App(root)
    root.mainloop()
