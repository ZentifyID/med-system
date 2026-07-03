"""Контроллер приложения: навигация и связывание страниц со слоем данных."""
import sqlite3
import tkinter as tk
from tkinter import messagebox

from PIL import Image
import customtkinter as ctk

from app import config
from app.db import (
    delete_employee, fetch_employee_by_id, fetch_employees_for_table, init_db, insert_employee, update_employee,
    fetch_students_for_table, fetch_student_by_id, insert_student, update_student, delete_student,
    fetch_groups, fetch_group_by_id, insert_group, update_group, delete_group,
    fetch_medicines_for_table, fetch_medicine_by_id, insert_medicine, update_medicine, delete_medicine,
    fetch_appeals_for_table, fetch_appeal_by_id, insert_appeal, update_appeal, delete_appeal,
    fetch_persons_for_combobox, get_next_appeal_number, search_icd_codes,
    fetch_all_icd_codes, insert_icd_code, update_icd_code, delete_icd_code,
    increment_first_digit_in_all_groups, check_and_auto_increment_groups,
    get_student_count_by_group, reorder_medicines,
)
from app.validators import get_person_expiration_status, get_medicine_expiration_status
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
from app.pages.delete_group_dialog import DeleteGroupDialog
from app.ui import (
    BG_SIDEBAR, BG_COLOR, TEXT_SIDEBAR, ACCENT, TEXT_COLOR, TEXT_MUTED,
    BORDER, SIDEBAR_BORDER,
    setup_styles, SidebarButton, show_toast,
)
from app.hotkeys import setup_global_undo


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_GEOMETRY)
        self.root.minsize(*config.WINDOW_MIN_SIZE)
        self.root.configure(bg=BG_COLOR)
        setup_styles(root)
        setup_global_undo(root)

        self.root.bind("<Escape>", self.handle_escape)
        self.root.bind("<Control-KeyPress>", self.handle_global_hotkeys)
        self.root.bind("<Return>", self.handle_enter)

        self.current_page = None
        self.search_query = ""
        self.filter_status = "Все сотрудники"
        self.search_query_students = ""
        self.filter_status_students = "Все студенты"
        self.search_query_medicines = ""
        self.filter_status_medicines = "Все лекарства"
        self.search_query_appeals = ""

        # ── Shell layout ──────────────────────────────────────────────
        shell = tk.Frame(root, bg=BG_COLOR)
        shell.pack(fill=tk.BOTH, expand=True)

        # Sidebar container (sidebar + right border line)
        sidebar_wrapper = tk.Frame(shell, bg=BG_SIDEBAR)
        sidebar_wrapper.pack(side=tk.LEFT, fill=tk.Y)

        self.sidebar = tk.Frame(sidebar_wrapper, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Thin right border (like Closure)
        tk.Frame(sidebar_wrapper, bg=SIDEBAR_BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Content
        self.content = tk.Frame(shell, bg=BG_COLOR)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Загрузка иконок для использования во всем приложении
        self.icons = self._load_icons()

        self._build_sidebar()
        self._build_pages()

        self.show_main_page()
        self.root.after(1000, self.auto_check_academic_year)

    def _load_icons(self) -> dict:
        def get_icon(name, emoji):
            path = config.ICONS_DIR / f"{name}.png"
            if path.exists():
                try:
                    return ctk.CTkImage(light_image=Image.open(path), size=(20, 20))
                except Exception:
                    return emoji
            return emoji

        return {
            "home":      get_icon("home",      "🏠"),
            "employees": get_icon("employees", "👤"),
            "students":  get_icon("students",  "🎓"),
            "medicine":  get_icon("medicine",  "💊"),
            "appeals":   get_icon("appeals",   "📋"),
            "search":    get_icon("search",    "🔍"),
        }

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> None:
        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(24, 20))

        tk.Label(
            logo_frame,
            text="⚕",
            font=("Segoe UI", 20),
            bg=BG_SIDEBAR,
            fg=ACCENT,
        ).pack(side=tk.LEFT, padx=(18, 8))

        tk.Label(
            logo_frame,
            text="MedSystem",
            font=("Segoe UI", 14, "bold"),
            bg=BG_SIDEBAR,
            fg=TEXT_COLOR,
        ).pack(side=tk.LEFT)

        # Nav buttons
        nav_items = [
            (self.icons["home"],      "Главная",     self.show_main_page),
            (self.icons["employees"], "Сотрудники",  self.show_employees_page),
            (self.icons["students"],  "Студенты",    self.show_students_page),
            (self.icons["medicine"],  "Лекарства",   self.show_medicines_page),
            (self.icons["appeals"],   "Обращения",   self.show_appeals_page),
        ]

        self._sidebar_buttons: dict[str, SidebarButton] = {}
        for icon, label, cmd in nav_items:
            btn = SidebarButton(self.sidebar, text=label, icon=icon, command=lambda c=cmd, l=label: self._nav_click(c, l))
            btn.pack(fill=tk.X, padx=10, pady=1)
            self._sidebar_buttons[label] = btn

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
        self.main_page = MainPage(
            c,
            on_employees=self.show_employees_page,
            on_students=self.show_students_page,
            on_medicines=self.show_medicines_page,
            on_appeals=self.show_appeals_page,
            on_add_employee=self.show_add_employee_page,
            on_add_student=self.show_add_student_page,
            on_add_medicine=self.show_add_medicine_page,
            on_add_appeal=self.show_add_appeal_page,
            icons=self.icons,
        )
        self.employees_page = EmployeesPage(c, on_add=self.show_add_employee_page, on_back=self.show_main_page, on_select=self.show_employee_view_page, on_delete=self.delete_employee_action, on_filter_changed=self.on_filter_changed, search_icon=self.icons["search"])
        self.employee_form_page = EmployeeFormPage(c, on_save=self.save_employee, on_cancel=self.show_employees_page)
        self.employee_view_page = EmployeeViewPage(c, on_save=self.edit_employee, on_delete=self.delete_employee_action, on_cancel=self.show_employees_page)

        self.students_page = StudentsPage(c, on_add=self.show_add_student_page, on_groups=self.show_groups_page, on_back=self.show_main_page, on_select=self.show_student_view_page, on_delete=self.delete_student_action, on_filter_changed=self.on_filter_changed_students, search_icon=self.icons["search"])
        self.student_form_page = StudentFormPage(c, on_save=self.save_student, on_cancel=self.show_students_page)
        self.student_view_page = StudentViewPage(c, on_save=self.edit_student, on_delete=self.delete_student_action, on_cancel=self.show_students_page)
        self.groups_page = GroupsPage(c, on_add=self.show_add_group_page, on_back=self.show_students_page, on_select=self.show_group_view_page, on_increment=self.manual_increment_groups_action, on_delete=self.delete_group_action)
        self.group_form_page = GroupFormPage(c, on_save=self.save_group, on_cancel=self.show_groups_page)
        self.group_view_page = GroupViewPage(c, on_save=self.edit_group, on_delete=self.delete_group_action, on_cancel=self.show_groups_page)

        self.medicines_page = MedicinesPage(c, on_add=self.show_add_medicine_page, on_back=self.show_main_page, on_select=self.show_medicine_view_page, on_delete=self.delete_medicine_action, on_order=self.order_medicines_action, on_filter_changed=self.on_filter_changed_medicines, search_icon=self.icons["search"])
        self.medicine_form_page = MedicineFormPage(c, on_save=self.save_medicine, on_cancel=self.show_medicines_page)
        self.medicine_view_page = MedicineViewPage(c, on_save=self.edit_medicine, on_delete=self.delete_medicine_action, on_cancel=self.show_medicines_page)

        self.appeals_page = AppealsPage(
            c, on_add=self.show_add_appeal_page, on_back=self.show_main_page, on_select=self.show_appeal_view_page,
            on_delete=self.delete_appeal_action, on_filter_changed=self.on_filter_changed_appeals, search_icon=self.icons["search"],
            fetch_icd_cb=fetch_all_icd_codes, insert_icd_cb=insert_icd_code, update_icd_cb=update_icd_code, delete_icd_cb=delete_icd_code
        )
        self.appeal_form_page = AppealFormPage(c, on_save=self.save_appeal, on_cancel=self.show_appeals_page, get_next_num_cb=get_next_appeal_number, search_icd_cb=search_icd_codes)
        self.appeal_view_page = AppealViewPage(c, on_save=self.edit_appeal, on_delete=self.delete_appeal_action, on_cancel=self.show_appeals_page, search_icd_cb=search_icd_codes)

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
        self.current_page = page

    def handle_escape(self, event) -> None:
        if self.current_page and hasattr(self.current_page, "back_button") and self.current_page.back_button.winfo_ismapped():
            self.current_page.back_button.invoke()
        elif self.current_page and hasattr(self.current_page, "_on_cancel"):
            self.current_page._on_cancel()


    def _is_text_input_widget(self, widget) -> bool:
        if widget is None:
            return False
        try:
            widget_class = widget.winfo_class()
        except tk.TclError:
            return False
        return isinstance(widget, (tk.Entry, tk.Text)) or widget_class in {"Entry", "Text", "TEntry", "TCombobox"}

    def _focus_entry(self, entry) -> None:
        entry.focus_set()
        inner_entry = entry._entry if hasattr(entry, "_entry") else entry
        try:
            inner_entry.focus_set()
            inner_entry.selection_range(0, tk.END)
            inner_entry.icursor(tk.END)
        except tk.TclError:
            pass

    def handle_global_hotkeys(self, event) -> str | None:
        keycode = getattr(event, "keycode", 0)
        keysym = getattr(event, "keysym", "").lower()
        if keycode == 70 or keysym == "f":
            self.handle_search_focus(event)
            return "break"
        if keycode == 83 or keysym == "s":
            return self.handle_save_shortcut()
        return None

    def handle_search_focus(self, event) -> None:
        if self.current_page and hasattr(self.current_page, "search_var"):
            search_entry = getattr(self.current_page, "search_entry", None)
            if search_entry is not None:
                self._focus_entry(search_entry)

    def handle_save_shortcut(self) -> str | None:
        if not self.current_page or not hasattr(self.current_page, "_submit"):
            return None
        if hasattr(self.current_page, "is_edit_mode") and not self.current_page.is_edit_mode:
            return None
        self.current_page._submit()
        return "break"

    def handle_enter(self, event) -> str | None:
        focus_widget = self.root.focus_get()
        if self._is_text_input_widget(focus_widget):
            return None

        if self.current_page and hasattr(self.current_page, "_open_selected"):
            table = getattr(self.current_page, "table", None)
            if table is not None:
                selection = table.selection()
                if focus_widget == table and selection:
                    self.current_page._open_selected()
                    return "break"

                children = table.get_children()
                if len(children) == 1:
                    table.selection_set(children[0])
                    self.current_page._open_selected()
                    return "break"
        return None

    def auto_check_academic_year(self) -> None:
        try:
            count = check_and_auto_increment_groups()
            if count > 0:
                show_toast(self.root, f"Начался новый учебный год! {count} групп переведены на следующий курс.", "info")
        except Exception:
            pass

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
        filtered = []
        for id, fio, affiliation, san_date, med_date, flu_date in rows:
            if self.search_query and self.search_query not in fio.lower():
                continue
            if self.filter_status != "Все сотрудники":
                is_expired, is_expiring = get_person_expiration_status([san_date, med_date, flu_date])
                if self.filter_status == "Просроченные" and not is_expired:
                    continue
                if self.filter_status == "Истекают (2 недели)" and not is_expiring:
                    continue
            filtered.append((id, fio, affiliation, san_date, med_date, flu_date))
        self.employees_page.set_rows(filtered)

    def save_employee(self, data: dict) -> None:
        try:
            insert_employee(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_employees_page()

    def edit_employee(self, employee_id: int, data: dict) -> None:
        try:
            update_employee(employee_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_employee_view_page(employee_id)

    def delete_employee_action(self, employee_id: int) -> None:
        try:
            delete_employee(employee_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
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
            show_toast(self.root, "Сначала добавьте хотя бы одну учебную группу.", "info")
            return
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
        filtered = []
        for id, fio, group_name, san_date, med_date, flu_date in rows:
            if self.search_query_students and self.search_query_students not in fio.lower():
                continue
            if self.filter_status_students != "Все студенты":
                is_expired, is_expiring = get_person_expiration_status([san_date, med_date, flu_date])
                if self.filter_status_students == "Просроченные" and not is_expired:
                    continue
                if self.filter_status_students == "Истекают (2 недели)" and not is_expiring:
                    continue
            filtered.append((id, fio, group_name, san_date, med_date, flu_date))
        self.students_page.set_rows(filtered)

    def save_student(self, data: dict) -> None:
        try:
            insert_student(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_students_page()

    def edit_student(self, student_id: int, data: dict) -> None:
        try:
            update_student(student_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_student_view_page(student_id)

    def delete_student_action(self, student_id: int) -> None:
        try:
            delete_student(student_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
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
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует.")
            return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_groups_page()

    def edit_group(self, group_id: int, name: str) -> None:
        try:
            update_group(group_id, name)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Группа с таким названием уже существует.")
            return
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_group_view_page(group_id)

    def delete_group_action(self, group_id: int) -> None:
        group_data = fetch_group_by_id(group_id)
        if not group_data: return

        student_count = get_student_count_by_group(group_id)

        if student_count > 0:
            def confirm_cascade():
                try:
                    delete_group(group_id, cascade=True)
                    show_toast(self.root, f"Группа '{group_data['name']}' и {student_count} чел. удалены.", "success")
                    self.show_groups_page()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")
            
            DeleteGroupDialog(self.root, group_data["name"], student_count, confirm_cascade)
        else:
            if messagebox.askyesno("Удаление", f"Удалить группу '{group_data['name']}'?"):
                try:
                    delete_group(group_id)
                    self.show_groups_page()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

    def manual_increment_groups_action(self) -> None:
        if messagebox.askyesno("Перевод на следующий курс", "Это увеличит первую цифру в названиях всех групп (например, 11 -> 21). Продолжить?"):
            try:
                count = increment_first_digit_in_all_groups()
                if count > 0:
                    show_toast(self.root, f"Готово! Обновлено групп: {count}", "success")
                    self.show_groups_page()
                else:
                    show_toast(self.root, "Нет подходящих групп для обновления.", "info")
            except Exception as exc:
                messagebox.showerror("Ошибка", f"Не удалось обновить группы: {exc}")

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
        filtered = []
        for id, name, dosage, qty, exp_date_str in rows:
            if self.search_query_medicines and self.search_query_medicines not in name.lower():
                continue
            is_expired, is_expiring = get_medicine_expiration_status(exp_date_str)
            is_low_qty = qty <= config.LOW_QUANTITY_THRESHOLD
            if self.filter_status_medicines == "Просроченные" and not is_expired:
                continue
            if self.filter_status_medicines == "Истекают (2 недели)" and not is_expiring:
                continue
            if self.filter_status_medicines == "Мало (<= 5)" and not is_low_qty:
                continue
            filtered.append((id, name, qty, dosage, exp_date_str, is_expiring, is_low_qty))
        self.medicines_page.set_rows(filtered)

    def save_medicine(self, data: dict) -> None:
        try:
            insert_medicine(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_medicines_page()

    def edit_medicine(self, medicine_id: int, data: dict) -> None:
        try:
            update_medicine(medicine_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_medicine_view_page(medicine_id)

    def delete_medicine_action(self, medicine_id: int) -> None:
        try:
            delete_medicine(medicine_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_medicines_page()

    def order_medicines_action(self) -> None:
        rows = fetch_medicines_for_table()
        to_order = []
        for id, name, dosage, qty, exp_date_str in rows:
            is_expired, is_expiring = get_medicine_expiration_status(exp_date_str)
            if qty <= config.LOW_QUANTITY_THRESHOLD or is_expiring:
                to_order.append({"id": id, "name": name, "dosage": dosage, "quantity": qty, "expiration_date": exp_date_str})
        if not to_order:
            show_toast(self.root, "Все лекарства в норме. Заказывать ничего не нужно.", "info")
            return
        OrderMedicinesDialog(self.root, to_order, self.confirm_order_medicines)

    def confirm_order_medicines(self, result: list) -> None:
        try:
            # Одна транзакция: при ошибке база останется нетронутой
            reorder_medicines(result)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.refresh_medicines_table()
        show_toast(self.root, "Заказ оформлен: старые партии списаны, новые добавлены.", "success")

    # ── Appeals ───────────────────────────────────────────────────────────────
    def show_appeals_page(self) -> None:
        self._set_active_nav("Обращения")
        self.refresh_appeals_table()
        self._show_page(self.appeals_page)

    def show_add_appeal_page(self) -> None:
        self._set_active_nav("Обращения")
        self.appeal_form_page.reset_form()
        self.appeal_form_page.set_senders(fetch_persons_for_combobox())
        self._show_page(self.appeal_form_page)

    def show_appeal_view_page(self, appeal_id: int) -> None:
        self._set_active_nav("Обращения")
        data = fetch_appeal_by_id(appeal_id)
        if data:
            self.appeal_view_page.set_senders(fetch_persons_for_combobox())
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
        for id, number, created_at, sender, complaints in rows:
            if self.search_query_appeals and (self.search_query_appeals not in str(number) and self.search_query_appeals not in sender.lower()):
                continue
            filtered.append((id, number, created_at, sender, complaints))
        self.appeals_page.set_rows(filtered)

    def save_appeal(self, data: dict) -> None:
        try:
            insert_appeal(data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_appeals_page()

    def edit_appeal(self, appeal_id: int, data: dict) -> None:
        try:
            update_appeal(appeal_id, data)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_appeal_view_page(appeal_id)

    def delete_appeal_action(self, appeal_id: int) -> None:
        try:
            delete_appeal(appeal_id)
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка базы данных", str(exc))
            return
        self.show_appeals_page()


def run_app() -> None:
    init_db()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = tk.Tk()
    App(root)
    root.mainloop()
