import os

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QComboBox, QMessageBox,
                             QTabWidget, QFormLayout, QGroupBox, QTextEdit,
                             QDateEdit, QSpinBox, QCheckBox, QDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from config.settings import Settings
from database import db
from user_manager import user_manager
from utils.helpers import get_file_size, apply_dialog_style
from widgets.backup_dialog import RestoreThread
from widgets.report_dialogs import ReportGenerationThread
from widgets.editors import TeacherEditor, StudentEditor, GradeEditor, ScheduleEditor, DisciplineEditor, StudyPlanEditor


class BasePanel(QWidget):
    """Базовый класс для всех ролевых панелей"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def create_table(self, headers, data=None):
        """Создание таблицы с заданными заголовками"""
        try:
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)

            # Устанавливаем режимы растягивания
            header = table.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #d0d0d0;
                    font-size: 13px;
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #f0f0f0;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    border: none;
                    font-size: 13px;
                }
            """)

            # Устанавливаем минимальную высоту строк
            table.verticalHeader().setDefaultSectionSize(45)

            if data:
                self.populate_table(table, data)

            return table

        except Exception as e:
            print(f"💥 Ошибка при создании таблицы: {e}")
            # Возвращаем простую таблицу в случае ошибки
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            return table

    def populate_table(self, table, data):
        """Заполнение таблицы данными"""
        try:
            if not data:
                table.setRowCount(0)
                return

            table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                    table.setItem(row_idx, col_idx, item)

        except Exception as e:
            print(f"💥 Ошибка при заполнении таблицы: {e}")
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("Ошибка загрузки данных"))

    def create_styled_group(self, title):
        """Создание стилизованной группы"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #3498db;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        return group

    def create_styled_button(self, text, color="#3498db"):
        """Создание стилизованной кнопки"""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """)
        return button

    def create_styled_input(self):
        """Создание стилизованного поля ввода"""
        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
        """)
        return input_field


class AdminPanel(BasePanel):
    """Панель администратора"""

    def __init__(self):
        super().__init__()
        apply_dialog_style(self)

    def setup_ui(self):
        super().setup_ui()

        # Заголовок
        title = QLabel("Панель администратора")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 10px;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)

        # Вкладка пользователей
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "👥 Пользователи")

        # Вкладка кафедр
        departments_tab = self.create_departments_tab()
        tabs.addTab(departments_tab, "🏢 Кафедры")

        # Вкладка системных логов
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "📋 Логи системы")

        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "💾 Резервные копии")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def create_users_tab(self):
        """Вкладка управления пользователями"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление пользователями")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        add_user_btn = self.create_styled_button("➕ Добавить пользователя")
        refresh_btn = self.create_styled_button("🔄 Обновить список")
        export_btn = self.create_styled_button("📊 Экспорт в CSV", "#27ae60")

        add_user_btn.clicked.connect(self.show_add_user_dialog)
        refresh_btn.clicked.connect(self.load_users)
        export_btn.clicked.connect(self.export_users)

        control_layout.addWidget(add_user_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(export_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица пользователей
        table_group = self.create_styled_group("Список пользователей")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.users_table = self.create_table([
            "ID", "Логин", "Роль", "Преподаватель", "Студент", "Статус", "Действия"
        ])
        table_layout.addWidget(self.users_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_departments_tab(self):
        """Вкладка управления кафедрами"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Форма добавления кафедры
        form_group = self.create_styled_group("Добавление новой кафедры")
        form_layout = QFormLayout()
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(15)

        self.dept_name_input = self.create_styled_input()
        self.dept_short_name_input = self.create_styled_input()

        self.dept_name_input.setPlaceholderText("Введите полное название кафедры")
        self.dept_short_name_input.setPlaceholderText("Введите сокращенное название")

        form_layout.addRow("📝 Название:", self.dept_name_input)
        form_layout.addRow("🏷️ Сокращение:", self.dept_short_name_input)

        add_btn = self.create_styled_button("✅ Добавить кафедру", "#27ae60")
        add_btn.clicked.connect(self.add_department)

        form_layout.addRow("", add_btn)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Таблица кафедр
        table_group = self.create_styled_group("Список кафедр")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.departments_table = self.create_table([
            "ID", "Название", "Сокращение", "Действия"
        ])
        self.departments_table.cellDoubleClicked.connect(self.on_department_action)
        table_layout.addWidget(self.departments_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_logs_tab(self):
        """Вкладка системных логов"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Системные логи")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображаются системные логи.\n"
            "Здесь можно отслеживать действия пользователей и системные события."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить логи")
        refresh_btn.clicked.connect(self.load_logs)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица логов
        table_group = self.create_styled_group("Последние 100 записей")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.logs_table = self.create_table([
            "ID", "Пользователь", "Таблица", "Действие", "Время", "ID записи"
        ])
        table_layout.addWidget(self.logs_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def load_users(self):
        """Загрузка пользователей с учетом возможного отсутствия столбца is_active"""
        try:
            # Пробуем запрос с is_active
            query = """
            SELECT u.id, u.login, u.role, 
                   COALESCE(t.fio, 'Не привязан'), 
                   COALESCE(s.fio, 'Не привязан'),
                   CASE WHEN u.is_active THEN 'Активен' ELSE 'Заблокирован' END as status
            FROM users u
            LEFT JOIN teachers t ON u.teacher_id = t.id
            LEFT JOIN students s ON u.student_id = s.id
            ORDER BY u.id
            """
            result = db.execute_query(query)
        except Exception as e:
            if 'is_active' in str(e):
                # Если столбец is_active не существует, используем запрос без него
                print("⚠️ Столбец is_active не найден, загружаем без статуса")
                query = """
                SELECT u.id, u.login, u.role, 
                       COALESCE(t.fio, 'Не привязан'), 
                       COALESCE(s.fio, 'Не привязан'),
                       'Активен' as status
                FROM users u
                LEFT JOIN teachers t ON u.teacher_id = t.id
                LEFT JOIN students s ON u.student_id = s.id
                ORDER BY u.id
                """
                result = db.execute_query(query)
            else:
                raise e

        if result:
            # Добавляем кнопки действий
            table_data = []
            for row in result:
                table_data.append(row + ("✏️ Удалить",))

            self.populate_table(self.users_table, table_data)

            # Подключаем обработчик двойного клика
            self.users_table.cellDoubleClicked.connect(self.on_user_action)

    def show_add_user_dialog(self):
        """Диалог добавления нового пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление пользователя")
        dialog.setFixedSize(400, 350)

        layout = QVBoxLayout()

        # Форма
        form_layout = QFormLayout()

        login_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        role_combo = QComboBox()
        teacher_combo = QComboBox()
        student_combo = QComboBox()
        status_checkbox = QCheckBox("Активный")
        status_checkbox.setChecked(True)

        # Заполняем роли
        role_combo.addItem("Выберите роль", None)
        role_combo.addItem("Администратор", "admin")
        role_combo.addItem("Сотрудник кафедры", "dekanat")
        role_combo.addItem("Преподаватель", "teacher")
        role_combo.addItem("Студент", "student")

        # Заполняем преподавателей
        teacher_combo.addItem("Не привязан", None)
        teachers = db.execute_query("SELECT id, fio FROM teachers ORDER BY fio")
        if teachers:
            for teacher_id, teacher_fio in teachers:
                teacher_combo.addItem(teacher_fio, teacher_id)

        # Заполняем студентов
        student_combo.addItem("Не привязан", None)
        students = db.execute_query("SELECT id, fio FROM students ORDER BY fio")
        if students:
            for student_id, student_fio in students:
                student_combo.addItem(student_fio, student_id)

        form_layout.addRow("Логин:", login_input)
        form_layout.addRow("Пароль:", password_input)
        form_layout.addRow("Роль:", role_combo)
        form_layout.addRow("Преподаватель:", teacher_combo)
        form_layout.addRow("Студент:", student_combo)
        form_layout.addRow("Статус:", status_checkbox)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_user():
            self.save_new_user(
                login_input.text().strip(),
                password_input.text(),
                role_combo.currentData(),
                teacher_combo.currentData(),
                student_combo.currentData(),
                status_checkbox.isChecked(),
                dialog
            )

        save_btn.clicked.connect(save_user)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        dialog.exec()

    def save_new_user(self, login, password, role, teacher_id, student_id, is_active, dialog):
        """Сохранение нового пользователя"""
        if not login or not password or not role:
            QMessageBox.warning(dialog, "Ошибка", "Заполните логин, пароль и выберите роль")
            return

        try:
            from user_manager import UserManager
            user_manager = UserManager()

            # Хешируем пароль
            hashed_password = user_manager.hash_password(password)

            # Получаем следующий ID (без использования последовательности)
            max_id_query = "SELECT COALESCE(MAX(id), 0) + 1 FROM users"
            result = db.execute_query(max_id_query)

            if result:
                next_id = result[0][0]

                # Вставляем пользователя (без is_active если столбца нет)
                try:
                    # Пробуем вставить с is_active
                    query = """
                    INSERT INTO users (id, login, password_hash, role, teacher_id, student_id, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    success = db.execute_query(query, (
                        next_id, login, hashed_password, role,
                        teacher_id, student_id, is_active
                    ), fetch=False)
                except Exception as e:
                    if 'is_active' in str(e):
                        # Если столбец is_active не существует, вставляем без него
                        print("⚠️ Столбец is_active не найден, вставляем без него")
                        query = """
                        INSERT INTO users (id, login, password_hash, role, teacher_id, student_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        success = db.execute_query(query, (
                            next_id, login, hashed_password, role,
                            teacher_id, student_id
                        ), fetch=False)
                    else:
                        raise e

                if success:
                    QMessageBox.information(dialog, "Успех", "Пользователь добавлен")
                    dialog.accept()
                    self.load_users()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось добавить пользователя")
            else:
                QMessageBox.warning(dialog, "Ошибка", "Не удалось получить ID для пользователя")

        except Exception as e:
            print(f"❌ Ошибка при добавлении пользователя: {e}")
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка при добавлении пользователя:\n{str(e)}")

    def on_user_action(self, row, column):
        """Обработка действий с пользователем"""
        if column == 6:  # Колонка "Действия"
            user_id = self.users_table.item(row, 0).text()
            user_login = self.users_table.item(row, 1).text()
            user_role = self.users_table.item(row, 2).text()

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Действия с пользователем: {user_login}")
            dialog.setFixedSize(500, 400)  # ← Увеличили размер

            layout = QVBoxLayout()
            layout.setContentsMargins(30, 30, 30, 30)  # ← Отступы
            layout.setSpacing(15)  # ← Отступы между элементами

            info_label = QLabel(f"Пользователь: {user_login}\nID: {user_id}\nРоль: {user_role}")
            info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 20px;")
            layout.addWidget(info_label)

            # Создаем группу кнопок
            buttons_layout = QVBoxLayout()
            buttons_layout.setSpacing(10)

            edit_login_btn = QPushButton("✏️ Изменить логин")
            edit_password_btn = QPushButton("✏️ Изменить пароль")
            edit_role_btn = QPushButton("✏️ Изменить роль")
            toggle_status_btn = QPushButton("🔄 Изменить статус")
            delete_btn = QPushButton("🗑️ Удалить пользователя")
            cancel_btn = QPushButton("Отмена")

            for btn in [edit_login_btn, edit_password_btn, edit_role_btn,
                        toggle_status_btn, delete_btn, cancel_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 12px 20px;
                        font-size: 13px;
                        font-weight: bold;
                        min-width: 200px;
                        text-align: left;
                    }
                    QPushButton:hover { background-color: #2980b9; }
                    QPushButton:pressed { background-color: #21618c; }
                """)
                btn.setMinimumHeight(40)

            edit_login_btn.clicked.connect(lambda: self.edit_user_login(user_id, user_login, dialog))
            edit_password_btn.clicked.connect(lambda: self.edit_user_password(user_id, user_login, dialog))
            edit_role_btn.clicked.connect(lambda: self.edit_user_role(user_id, user_login, user_role, dialog))
            toggle_status_btn.clicked.connect(lambda: self.toggle_user_status(user_id, user_login, dialog))
            delete_btn.clicked.connect(lambda: self.delete_user(user_id, user_login, dialog))
            cancel_btn.clicked.connect(dialog.reject)

            buttons_layout.addWidget(edit_login_btn)
            buttons_layout.addWidget(edit_password_btn)
            buttons_layout.addWidget(edit_role_btn)
            buttons_layout.addWidget(toggle_status_btn)
            buttons_layout.addWidget(delete_btn)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)
            dialog.setLayout(layout)
            dialog.exec()

    def edit_user_login(self, user_id, current_login, parent_dialog):
        """Изменение логина пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменение логина пользователя")
        dialog.setFixedSize(400, 150)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        login_input = QLineEdit()
        login_input.setText(current_login)
        login_input.selectAll()

        form_layout.addRow("Новый логин:", login_input)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_changes():
            new_login = login_input.text().strip()
            if not new_login:
                QMessageBox.warning(dialog, "Ошибка", "Введите логин пользователя")
                return

            if new_login == current_login:
                QMessageBox.information(dialog, "Информация", "Логин не изменился")
                dialog.reject()
                return

            # Проверяем уникальность логина
            check_query = "SELECT COUNT(*) FROM users WHERE login = %s AND id != %s"
            result = db.execute_query(check_query, (new_login, user_id))

            if result and result[0][0] > 0:
                QMessageBox.warning(dialog, "Ошибка", "Пользователь с таким логином уже существует")
                return

            try:
                query = "UPDATE users SET login = %s WHERE id = %s"
                success = db.execute_query(query, (new_login, user_id), fetch=False)

                if success:
                    QMessageBox.information(dialog, "Успех", "Логин пользователя обновлен")
                    dialog.accept()
                    parent_dialog.accept()
                    self.load_users()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить логин")

            except Exception as e:
                print(f"❌ Ошибка при изменении логина: {e}")
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при изменении логина:\n{str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def edit_user_password(self, user_id, user_login, parent_dialog):
        """Изменение пароля пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Изменение пароля: {user_login}")
        dialog.setFixedSize(400, 200)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_input = QLineEdit()
        confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Новый пароль:", password_input)
        form_layout.addRow("Подтверждение:", confirm_input)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_changes():
            password = password_input.text()
            confirm = confirm_input.text()

            if not password:
                QMessageBox.warning(dialog, "Ошибка", "Введите пароль")
                return

            if password != confirm:
                QMessageBox.warning(dialog, "Ошибка", "Пароли не совпадают")
                return

            try:
                from user_manager import UserManager
                user_manager = UserManager()
                hashed_password = user_manager.hash_password(password)

                query = "UPDATE users SET password_hash = %s WHERE id = %s"
                success = db.execute_query(query, (hashed_password, user_id), fetch=False)

                if success:
                    QMessageBox.information(dialog, "Успех", "Пароль пользователя обновлен")
                    dialog.accept()
                    parent_dialog.accept()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить пароль")

            except Exception as e:
                print(f"❌ Ошибка при изменении пароля: {e}")
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при изменении пароля:\n{str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def edit_user_role(self, user_id, user_login, current_role, parent_dialog):
        """Изменение роли пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Изменение роли: {user_login}")
        dialog.setFixedSize(400, 150)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        role_combo = QComboBox()

        role_combo.addItem("Администратор", "admin")
        role_combo.addItem("Сотрудник кафедры", "dekanat")
        role_combo.addItem("Преподаватель", "teacher")
        role_combo.addItem("Студент", "student")

        # Устанавливаем текущую роль
        index = role_combo.findData(current_role)
        if index >= 0:
            role_combo.setCurrentIndex(index)

        form_layout.addRow("Новая роль:", role_combo)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_changes():
            new_role = role_combo.currentData()

            if new_role == current_role:
                QMessageBox.information(dialog, "Информация", "Роль не изменилась")
                dialog.reject()
                return

            try:
                query = "UPDATE users SET role = %s WHERE id = %s"
                success = db.execute_query(query, (new_role, user_id), fetch=False)

                if success:
                    QMessageBox.information(dialog, "Успех", "Роль пользователя обновлена")
                    dialog.accept()
                    parent_dialog.accept()
                    self.load_users()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить роль")

            except Exception as e:
                print(f"❌ Ошибка при изменении роли: {e}")
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при изменении роли:\n{str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def toggle_user_status(self, user_id, user_login, parent_dialog):
        """Изменение статуса пользователя (активен/заблокирован)"""
        try:
            # Получаем текущий статус
            query = "SELECT is_active FROM users WHERE id = %s"
            result = db.execute_query(query, (user_id,))

            if not result:
                QMessageBox.warning(parent_dialog, "Ошибка", "Не удалось получить данные пользователя")
                return

            current_status = result[0][0]
            new_status = not current_status

            action = "разблокировать" if new_status else "заблокировать"

            reply = QMessageBox.question(
                parent_dialog,
                "Подтверждение",
                f"Вы уверены, что хотите {action} пользователя?\n\n"
                f"Логин: {user_login}\n"
                f"ID: {user_id}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                query = "UPDATE users SET is_active = %s WHERE id = %s"
                success = db.execute_query(query, (new_status, user_id), fetch=False)

                if success:
                    status_text = "разблокирован" if new_status else "заблокирован"
                    QMessageBox.information(parent_dialog, "Успех", f"Пользователь {status_text}")
                    parent_dialog.accept()
                    self.load_users()
                else:
                    QMessageBox.warning(parent_dialog, "Ошибка", f"Не удалось {action} пользователя")

        except Exception as e:
            print(f"❌ Ошибка при изменении статуса пользователя: {e}")
            QMessageBox.critical(parent_dialog, "Ошибка", f"Ошибка при изменении статуса:\n{str(e)}")

    def delete_user(self, user_id, user_login, parent_dialog):
        """Удаление пользователя"""
        reply = QMessageBox.question(
            parent_dialog,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить пользователя?\n\n"
            f"Логин: {user_login}\n"
            f"ID: {user_id}\n\n"
            f"Это действие нельзя отменить!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM users WHERE id = %s"
                success = db.execute_query(query, (user_id,), fetch=False)

                if success:
                    QMessageBox.information(parent_dialog, "Успех", "Пользователь удален")
                    parent_dialog.accept()
                    self.load_users()
                else:
                    QMessageBox.warning(parent_dialog, "Ошибка", "Не удалось удалить пользователя")

            except Exception as e:
                print(f"❌ Ошибка при удалении пользователя: {e}")
                QMessageBox.critical(parent_dialog, "Ошибка", f"Ошибка при удалении пользователя:\n{str(e)}")

    def export_users(self):
        """Экспорт списка пользователей"""
        try:
            from datetime import datetime
            import csv

            # Получаем данные пользователей
            query = """
            SELECT u.id, u.login, u.role, u.is_active,
                   COALESCE(t.fio, ''), 
                   COALESCE(s.fio, ''),
                   u.created_at
            FROM users u
            LEFT JOIN teachers t ON u.teacher_id = t.id
            LEFT JOIN students s ON u.student_id = s.id
            ORDER BY u.id
            """
            users_data = db.execute_query(query)

            if not users_data:
                QMessageBox.information(self, "Информация", "Нет данных для экспорта")
                return

            # Сохраняем в CSV
            backup_dir = os.path.join(Settings.REPORTS_DIR, 'exports')
            os.makedirs(backup_dir, exist_ok=True)

            filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = os.path.join(backup_dir, filename)

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['ID', 'Логин', 'Роль', 'Статус', 'Преподаватель', 'Студент', 'Дата создания'])

                for user in users_data:
                    status = 'Активен' if user[3] else 'Заблокирован'
                    writer.writerow([user[0], user[1], user[2], status, user[4], user[5], user[6]])

            QMessageBox.information(self, "Успех", f"Данные экспортированы в файл:\n{file_path}")

        except Exception as e:
            print(f"❌ Ошибка при экспорте пользователей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте:\n{str(e)}")

    def add_department(self):
        """Добавление новой кафедры с автоматическим ID"""
        name = self.dept_name_input.text().strip()
        short_name = self.dept_short_name_input.text().strip()

        if not name or not short_name:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            # Получаем следующий ID из последовательности
            id_query = "SELECT nextval('departments_id_seq')"
            result = db.execute_query(id_query)

            if not result:
                # Если последовательности нет, находим максимальный ID и добавляем 1
                max_id_query = "SELECT COALESCE(MAX(id), 0) + 1 FROM departments"
                result = db.execute_query(max_id_query)

            if result:
                next_id = result[0][0]

                # Вставляем с явным указанием ID
                query = """
                INSERT INTO departments (id, name, short_name, created_at) 
                VALUES (%s, %s, %s, NOW())
                """
                success = db.execute_query(query, (next_id, name, short_name), fetch=False)

                if success:
                    QMessageBox.information(self, "Успех", "Кафедра добавлена")
                    self.dept_name_input.clear()
                    self.dept_short_name_input.clear()
                    self.load_departments()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить кафедру")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить ID для кафедры")

        except Exception as e:
            print(f"❌ Ошибка при добавлении кафедры: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении кафедры:\n{str(e)}")

    def load_departments(self):
        """Загрузка кафедр с кнопками действий"""
        query = "SELECT id, name, short_name FROM departments ORDER BY id"
        result = db.execute_query(query)
        if result:
            # Добавляем кнопки действий
            table_data = []
            for row in result:
                table_data.append(row + ("✏️ 🗑️",))  # Редактировать и Удалить

            self.populate_table(self.departments_table, table_data)

    def on_department_action(self, row, column):
        """Обработка действий с кафедрой"""
        if column == 3:  # Колонка "Действия"
            department_id = self.departments_table.item(row, 0).text()
            department_name = self.departments_table.item(row, 1).text()
            # Диалог выбора действия
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Действия с кафедрой: {department_name}")
            dialog.setFixedSize(450, 300)  # ← Увеличили размер

            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(30, 30, 30, 30)
            main_layout.setSpacing(15)

            # Заголовок
            info_label = QLabel(f"Кафедра: {department_name}\nID: {department_id}")
            info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 20px;")
            main_layout.addWidget(info_label)

            # Кнопки
            button_style = """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 350px;
                    text-align: left;
                }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton:pressed { background-color: #21618c; }
            """

            edit_name_btn = QPushButton("✏️ Изменить название")
            edit_short_btn = QPushButton("✏️ Изменить сокращение")
            delete_btn = QPushButton("🗑️ Удалить кафедру")
            cancel_btn = QPushButton("Отмена")

            for btn in [edit_name_btn, edit_short_btn, delete_btn, cancel_btn]:
                btn.setStyleSheet(button_style)
                btn.setMinimumHeight(40)

            edit_name_btn.clicked.connect(lambda: self.edit_department_name(department_id, department_name, dialog))
            edit_short_btn.clicked.connect(
                lambda: self.edit_department_short_name(department_id, department_name, dialog))
            delete_btn.clicked.connect(lambda: self.delete_department(department_id, department_name, dialog))
            cancel_btn.clicked.connect(dialog.reject)

            main_layout.addWidget(edit_name_btn)
            main_layout.addWidget(edit_short_btn)
            main_layout.addWidget(delete_btn)
            main_layout.addStretch()  # ← растягиваем пространство
            main_layout.addWidget(cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)

            dialog.setLayout(main_layout)
            dialog.exec()

    def edit_department_name(self, department_id, current_name, parent_dialog):
        """Изменение названия кафедры"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменение названия кафедры")
        dialog.setFixedSize(400, 150)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        name_input = QLineEdit()
        name_input.setText(current_name)
        name_input.selectAll()

        form_layout.addRow("Новое название:", name_input)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_changes():
            new_name = name_input.text().strip()
            if not new_name:
                QMessageBox.warning(dialog, "Ошибка", "Введите название кафедры")
                return

            if new_name == current_name:
                QMessageBox.information(dialog, "Информация", "Название не изменилось")
                dialog.reject()
                return

            try:
                query = "UPDATE departments SET name = %s WHERE id = %s"
                success = db.execute_query(query, (new_name, department_id), fetch=False)

                if success:
                    QMessageBox.information(dialog, "Успех", "Название кафедры обновлено")
                    dialog.accept()
                    parent_dialog.accept()
                    self.load_departments()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить название")

            except Exception as e:
                print(f"❌ Ошибка при изменении названия кафедры: {e}")
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при изменении названия:\n{str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def edit_department_short_name(self, department_id, department_name, parent_dialog):
        """Изменение сокращения кафедры"""
        # Получаем текущее сокращение
        query = "SELECT short_name FROM departments WHERE id = %s"
        result = db.execute_query(query, (department_id,))
        if not result:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные кафедры")
            return

        current_short_name = result[0][0]

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Изменение сокращения: {department_name}")
        dialog.setFixedSize(400, 150)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        short_name_input = QLineEdit()
        short_name_input.setText(current_short_name)
        short_name_input.selectAll()

        form_layout.addRow("Новое сокращение:", short_name_input)
        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        def save_changes():
            new_short_name = short_name_input.text().strip()
            if not new_short_name:
                QMessageBox.warning(dialog, "Ошибка", "Введите сокращение кафедры")
                return

            if new_short_name == current_short_name:
                QMessageBox.information(dialog, "Информация", "Сокращение не изменилось")
                dialog.reject()
                return

            try:
                query = "UPDATE departments SET short_name = %s WHERE id = %s"
                success = db.execute_query(query, (new_short_name, department_id), fetch=False)

                if success:
                    QMessageBox.information(dialog, "Успех", "Сокращение кафедры обновлено")
                    dialog.accept()
                    parent_dialog.accept()
                    self.load_departments()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить сокращение")

            except Exception as e:
                print(f"❌ Ошибка при изменении сокращения кафедры: {e}")
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при изменении сокращения:\n{str(e)}")

        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def delete_department(self, department_id, department_name, parent_dialog):
        """Удаление кафедры"""
        # Проверяем, есть ли связанные преподаватели
        check_query = "SELECT COUNT(*) FROM teachers WHERE department_id = %s"
        result = db.execute_query(check_query, (department_id,))

        if result and result[0][0] > 0:
            QMessageBox.warning(
                parent_dialog,
                "Ошибка",
                f"Нельзя удалить кафедру '{department_name}'\n\n"
                f"На кафедре числятся преподаватели.\n"
                f"Сначала переместите или удалите преподавателей."
            )
            return

        reply = QMessageBox.question(
            parent_dialog,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить кафедру?\n\n"
            f"Название: {department_name}\n"
            f"ID: {department_id}\n\n"
            f"Это действие нельзя отменить!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM departments WHERE id = %s"
                success = db.execute_query(query, (department_id,), fetch=False)

                if success:
                    QMessageBox.information(parent_dialog, "Успех", "Кафедра удалена")
                    parent_dialog.accept()
                    self.load_departments()
                else:
                    QMessageBox.warning(parent_dialog, "Ошибка", "Не удалось удалить кафедру")

            except Exception as e:
                print(f"❌ Ошибка при удалении кафедры: {e}")
                QMessageBox.critical(parent_dialog, "Ошибка", f"Ошибка при удалении кафедры:\n{str(e)}")

    def load_logs(self):
        """Загрузка логов"""
        try:
            # Проверяем существование таблицы audit_logs
            check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'audit_logs'
            );
            """
            table_exists = db.execute_query(check_query)

            if table_exists and table_exists[0][0]:
                query = """
                SELECT id, user_name, table_name, action_type, action_time, record_id 
                FROM audit_logs 
                ORDER BY action_time DESC 
                LIMIT 100
                """
                result = db.execute_query(query)
            else:
                # Если таблицы нет, создаем тестовые данные
                result = [
                    [1, 'admin', 'users', 'INSERT', '2024-01-01 10:00:00', 1],
                    [2, 'teacher', 'grades', 'UPDATE', '2024-01-01 11:00:00', 5]
                ]

            if result:
                self.populate_table(self.logs_table, result)
        except Exception as e:
            print(f"❌ Ошибка при загрузке логов: {e}")
            # Создаем тестовые данные при ошибке
            test_data = [
                [1, 'admin', 'users', 'INSERT', '2024-01-01 10:00:00', 1],
                [2, 'teacher', 'grades', 'UPDATE', '2024-01-01 11:00:00', 5]
            ]
            self.populate_table(self.logs_table, test_data)

    def create_backup_tab(self):
        """Вкладка управления резервными копиями"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информация о БД
        info_group = self.create_styled_group("Информация о базе данных")
        info_layout = QFormLayout()
        info_layout.setContentsMargins(25, 25, 25, 25)
        info_layout.setSpacing(15)

        self.db_size_label = QLabel("Загрузка...")
        self.db_tables_label = QLabel("Загрузка...")
        self.last_backup_label = QLabel("Загрузка...")

        # Стили для меток информации
        info_style = """
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
        """
        self.db_size_label.setStyleSheet(info_style)
        self.db_tables_label.setStyleSheet(info_style)
        self.last_backup_label.setStyleSheet(info_style)

        info_layout.addRow("💾 Размер базы данных:", self.db_size_label)
        info_layout.addRow("📊 Количество таблиц:", self.db_tables_label)
        info_layout.addRow("🕐 Последний бэкап:", self.last_backup_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Кнопки управления
        button_group = self.create_styled_group("Управление резервными копиями")
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(25, 25, 25, 25)
        button_layout.setSpacing(15)

        backup_btn = self.create_styled_button("💾 Создать резервную копию")
        manage_btn = self.create_styled_button("📁 Управление бэкапами")
        vacuum_btn = self.create_styled_button("⚡ Оптимизировать БД", "#e67e22")

        backup_btn.clicked.connect(self.create_backup)
        manage_btn.clicked.connect(self.manage_backups)
        vacuum_btn.clicked.connect(self.optimize_database)

        button_layout.addWidget(backup_btn)
        button_layout.addWidget(manage_btn)
        button_layout.addWidget(vacuum_btn)

        button_group.setLayout(button_layout)
        layout.addWidget(button_group)

        # Загрузка информации при открытии вкладки
        self.load_database_info()

        widget.setLayout(layout)
        return widget

    def load_database_info(self):
        """Загрузка информации о базе данных"""
        try:
            # Размер БД
            size_query = """
               SELECT pg_size_pretty(pg_database_size(current_database()))
               """
            size_result = db.execute_query(size_query)
            if size_result:
                self.db_size_label.setText(size_result[0][0])

            # Количество таблиц
            tables_query = """
               SELECT COUNT(*) FROM information_schema.tables 
               WHERE table_schema = 'public'
               """
            tables_result = db.execute_query(tables_query)
            if tables_result:
                self.db_tables_label.setText(str(tables_result[0][0]))

            # Последний бэкап
            from services.backup_service import BackupService
            backups = BackupService.get_backup_list()
            if backups:
                self.last_backup_label.setText(backups[0]['created'])
            else:
                self.last_backup_label.setText("Нет бэкапов")

        except Exception as e:
            self.db_size_label.setText("Ошибка")
            self.db_tables_label.setText("Ошибка")
            self.last_backup_label.setText("Ошибка")

    def create_backup(self):
        """Создание резервной копии - полная версия"""
        try:
            print("🔄 ПОЛНОЦЕННОЕ СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ")

            from services.backup_service import BackupService

            progress = QProgressDialog("Создание резервной копии...", "Отмена", 0, 0, self)
            progress.setWindowTitle("Пожалуйста, подождите")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setFixedSize(400, 120)
            progress.show()

            # Создаем бэкап (автоматически выберет лучший метод)
            print("🎯 Запускаем создание бэкапа...")
            backup_file = BackupService.create_backup()

            progress.close()

            if backup_file:
                file_size = os.path.getsize(backup_file)
                print(f"✅ Резервная копия создана: {backup_file} ({file_size} bytes)")

                QMessageBox.information(self, "Успех",
                                        f"Резервная копия успешно создана!\n\n"
                                        f"Метод: {'pg_dump' if 'pg_dump' in backup_file else 'Python'}\n"
                                        f"Файл: {os.path.basename(backup_file)}\n"
                                        f"Размер: {file_size} байт\n"
                                        f"Путь: {backup_file}")
                self.load_database_info()
            else:
                print("❌ Не удалось создать резервную копию")
                QMessageBox.critical(self, "Ошибка",
                                     "Не удалось создать резервную копию\n\n"
                                     "Все методы создания бэкапа завершились ошибкой.\n"
                                     "Проверьте:\n"
                                     "• Подключение к базе данных\n"
                                     "• Права на запись файлов\n"
                                     "• Доступность pg_dump (для ускорения)")

        except Exception as e:
            print(f"💥 Ошибка при создании бэкапа: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию:\n{str(e)}")

    def on_backup_created(self, file_path, progress):
        """Обработка успешного создания бэкапа"""
        progress.close()
        QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{file_path}")
        self.load_database_info()

    def on_backup_error(self, error, progress):
        """Обработка ошибки создания бэкапа"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию:\n{error}")

    def restore_backup(self):
        """Восстановление из резервной копии с улучшенной диагностикой"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите резервную копию для восстановления")
            return

        backup_data = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение восстановления",
            f"ВНИМАНИЕ: Это действие НЕОБРАТИМО!\n\n"
            f"Вы уверены, что хотите восстановить базу данных?\n"
            f"Файл: {backup_data['filename']}\n"
            f"Размер: {get_file_size(backup_data['path'])}\n"
            f"Создан: {backup_data['created']}\n\n"
            f"⚠️  Все текущие данные будут УДАЛЕНЫ и заменены данными из бэкапа!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # По умолчанию "Нет" для безопасности
        )

        if reply == QMessageBox.StandardButton.Yes:
            progress = QProgressDialog("Восстановление базы данных...", "Отмена", 0, 0, self)
            progress.setWindowTitle("Пожалуйста, подождите")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setFixedSize(500, 150)
            progress.show()

            # Запускаем восстановление в отдельном потоке
            self.restore_thread = RestoreThread(backup_data['path'])
            self.restore_thread.finished.connect(lambda success: self.on_restore_finished(success, progress))
            self.restore_thread.error.connect(lambda error: self.on_restore_error(error, progress))
            self.restore_thread.start()

    def on_restore_finished(self, success, progress):
        """Обработка завершения восстановления"""
        progress.close()

        if success:
            QMessageBox.information(self, "Успех",
                                    "База данных успешно восстановлена из резервной копии!\n\n"
                                    "Рекомендуется:\n"
                                    "• Перезапустить приложение\n"
                                    "• Проверить целостность данных")
        else:
            QMessageBox.critical(self, "Ошибка",
                                 "Не удалось восстановить базу данных\n\n"
                                 "Возможные причины:\n"
                                 "• Несовместимость формата бэкапа\n"
                                 "• Ошибки в SQL скрипте\n"
                                 "• Проблемы с подключением к БД\n\n"
                                 "Проверьте консоль для детальной информации.")

    def on_restore_error(self, error, progress):
        """Обработка ошибки восстановления"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Ошибка при восстановлении:\n{error}")

    def manage_backups(self):
        """Управление резервными копиями"""
        from widgets.backup_dialog import BackupDialog
        dialog = BackupDialog(self)
        dialog.exec()
        self.load_database_info()

    def optimize_database(self):
        """Оптимизация базы данных"""
        reply = QMessageBox.question(
            self,
            "Оптимизация базы данных",
            "Выполнить оптимизацию (VACUUM ANALYZE) базы данных?\n\n"
            "Эта операция:\n"
            "• Улучшит производительность БД\n"
            "• Освободит занятое место\n"
            "• Обновит статистику для оптимизатора\n"
            "• Может занять некоторое время\n\n"
            "Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                progress = QProgressDialog("Оптимизация базы данных...\nЭто может занять несколько минут.",
                                           "Отмена", 0, 0, self)
                progress.setWindowTitle("Пожалуйста, подождите")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setFixedSize(500, 150)
                progress.show()

                # Даем прогресс-диалогу время отобразиться
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, self._perform_optimization)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось запустить оптимизацию:\n{str(e)}")

    def _perform_optimization(self):
        """Выполнение оптимизации базы данных"""
        try:
            print("🔧 ЗАПУСК ОПТИМИЗАЦИИ БАЗЫ ДАННЫХ")

            # Используем метод без транзакции
            success = db.execute_without_transaction("VACUUM ANALYZE")

            if success:
                print("✅ Оптимизация базы данных завершена")
                self.load_database_info()
                QMessageBox.information(self, "Успех", "Оптимизация базы данных завершена успешно!")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось выполнить оптимизацию базы данных")

        except Exception as e:
            print(f"💥 Ошибка при оптимизации БД: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось оптимизировать БД:\n{str(e)}")

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_users()
        self.load_departments()
        self.load_logs()

class DekanatPanel(BasePanel):
    """Панель сотрудника кафедры"""

    def __init__(self):
        super().__init__()

    def setup_ui(self):
        super().setup_ui()

        title = QLabel("Панель сотрудника кафедры")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 10px;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)

        # Дисциплины кафедры
        disciplines_tab = self.create_disciplines_tab()
        tabs.addTab(disciplines_tab, "📚 Дисциплины")

        # Учебные планы
        plans_tab = self.create_study_plans_tab()
        tabs.addTab(plans_tab, "📋 Учебные планы")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Расписание")

        # Студенты
        students_tab = self.create_students_tab()
        tabs.addTab(students_tab, "👥 Студенты")

        # Преподаватели
        teachers_tab = self.create_teachers_tab()
        tabs.addTab(teachers_tab, "👨‍🏫 Преподаватели")

        # Отчеты
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def load_initial_data(self):
        """Загрузка начальных данных"""
        print("🔄 Начало загрузки данных для DekanatPanel")
        try:
            self.load_groups()
            print("✅ Группы загружены")
            self.load_students()
            print("✅ Студенты загружены")
            self.load_teachers()
            print("✅ Преподаватели загружены")
            self.load_disciplines()
            print("✅ Дисциплины загружены")
            self.load_study_plans()
            print("✅ Учебные планы загружены")
            self.load_schedule()
            print("✅ Расписание загружено")
        except Exception as e:
            print(f"💥 Ошибка при загрузке данных: {e}")
            import traceback
            traceback.print_exc()

    def create_teachers_tab(self):
        """Вкладка управления преподавателями"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление преподавателями")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        add_teacher_btn = self.create_styled_button("➕ Добавить преподавателя")
        refresh_btn = self.create_styled_button("🔄 Обновить список")

        add_teacher_btn.clicked.connect(self.add_teacher)
        refresh_btn.clicked.connect(self.load_teachers)

        control_layout.addWidget(add_teacher_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица преподавателей
        table_group = self.create_styled_group("Преподаватели кафедры")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.teachers_table = self.create_table([
            "ID", "ФИО", "Должность", "Учёная степень", "Кафедра", "Действия"
        ])
        self.teachers_table.cellDoubleClicked.connect(self.on_teacher_action)
        table_layout.addWidget(self.teachers_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_disciplines_tab(self):
        """Вкладка управления дисциплинами кафедры"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление дисциплинами")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        add_discipline_btn = self.create_styled_button("➕ Добавить дисциплину")
        refresh_btn = self.create_styled_button("🔄 Обновить список")

        add_discipline_btn.clicked.connect(self.add_discipline)
        refresh_btn.clicked.connect(self.load_disciplines)

        control_layout.addWidget(add_discipline_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица дисциплин
        table_group = self.create_styled_group("Дисциплины кафедры")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.disciplines_table = self.create_table([
            "ID", "Название", "Кафедра", "Действия"
        ])
        self.disciplines_table.cellDoubleClicked.connect(self.on_discipline_action)
        table_layout.addWidget(self.disciplines_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def load_disciplines(self):
        role = user_manager.current_user['role']
        dept_id = user_manager.current_user.get('department_id')

        if role == 'kafedra' and not dept_id:
            QMessageBox.warning(self, "Ошибка", "Не указана кафедра пользователя")
            return

        if role == 'kafedra':
            query = """
            SELECT d.id, d.name, dep.name
            FROM disciplines d
            JOIN departments dep ON d.department_id = dep.id
            WHERE d.department_id = %s
            ORDER BY d.name
            """
            result = db.execute_query(query, (dept_id,))
        else:  # admin
            query = """
            SELECT d.id, d.name, dep.name
            FROM disciplines d
            JOIN departments dep ON d.department_id = dep.id
            ORDER BY d.name
            """
            result = db.execute_query(query)

        if result:
            table_data = [row + ("✏️ 🗑️",) for row in result]
            self.populate_table(self.disciplines_table, table_data)
        else:
            self.disciplines_table.setRowCount(1)
            self.disciplines_table.setItem(0, 0, QTableWidgetItem("Нет данных"))

    def add_discipline(self):
        """Добавление новой дисциплины"""
        from widgets.editors import DisciplineEditor
        editor = DisciplineEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_disciplines()

    def on_discipline_action(self, row, column):
        """Обработка действий с дисциплиной"""
        if column == 3:  # Колонка "Действия"
            discipline_id = self.disciplines_table.item(row, 0).text()
            discipline_name = self.disciplines_table.item(row, 1).text()
            department_name = self.disciplines_table.item(row, 2).text()

            # Получаем department_id
            query = "SELECT id FROM departments WHERE name = %s"
            result = db.execute_query(query, (department_name,))
            department_id = result[0][0] if result else None

            discipline_data = (discipline_id, discipline_name, department_id)

            from widgets.editors import DisciplineEditor
            editor = DisciplineEditor(discipline_data, parent=self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                self.load_disciplines()

    def add_study_plan(self):
        """Добавление нового учебного плана"""
        from widgets.editors import StudyPlanEditor
        editor = StudyPlanEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_study_plans()

    def on_plan_action(self, row, column):
        if column == 7:  # Колонка "Действия"
            plan_id = int(self.plans_table.item(row, 0).text())
            discipline_name = self.plans_table.item(row, 1).text()
            group_name = self.plans_table.item(row, 2).text()
            teacher_name = self.plans_table.item(row, 3).text()
            semester = int(self.plans_table.item(row, 4).text())
            lect = int(self.plans_table.item(row, 5).text())
            pract = int(self.plans_table.item(row, 6).text())

            # Получаем ID по именам
            disc_id = self._get_discipline_id_by_name(discipline_name)
            group_id = self._get_group_id_by_name(group_name)
            teacher_id = self._get_teacher_id_by_name(teacher_name)

            if disc_id is None or group_id is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID сущностей")
                return

            plan_data = (plan_id, disc_id, group_id, teacher_id, semester, lect, pract)

            # Диалог выбора действия
            action = QMessageBox.question(
                self, "Действие",
                "Выберите действие:\n✅ — Редактировать\n🗑️ — Удалить",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if action == QMessageBox.StandardButton.Yes:
                # Редактировать
                from widgets.editors import StudyPlanEditor
                editor = StudyPlanEditor(plan_data=plan_data, parent=self)
                if editor.exec() == QDialog.DialogCode.Accepted:
                    self.load_study_plans()
            elif action == QMessageBox.StandardButton.No:
                # Удалить
                reply = QMessageBox.warning(
                    self, "Подтверждение",
                    f"Удалить учебный план?\nДисциплина: {discipline_name}\nГруппа: {group_name}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    db.execute_query("DELETE FROM study_plans WHERE id = %s", (plan_id,), fetch=False)
                    self.load_study_plans()

    def create_study_plans_tab(self):
        """Вкладка управления учебными планами"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление учебными планами")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        add_plan_btn = self.create_styled_button("➕ Добавить учебный план")
        refresh_btn = self.create_styled_button("🔄 Обновить планы")

        add_plan_btn.clicked.connect(self.add_study_plan)
        refresh_btn.clicked.connect(self.load_study_plans)

        control_layout.addWidget(add_plan_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица учебных планов
        table_group = self.create_styled_group("Учебные планы")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.plans_table = self.create_table([
            "ID", "Дисциплина", "Группа", "Преподаватель", "Семестр", "Лекции (ч)", "Практика (ч)", "Действия"
        ])
        self.plans_table.cellDoubleClicked.connect(self.on_plan_action)
        table_layout.addWidget(self.plans_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        """Вкладка управления расписанием"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление расписанием")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        add_schedule_btn = self.create_styled_button("➕ Добавить занятие")
        refresh_btn = self.create_styled_button("🔄 Обновить расписание")

        add_schedule_btn.clicked.connect(self.add_schedule)
        refresh_btn.clicked.connect(self.load_schedule)

        control_layout.addWidget(add_schedule_btn)
        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица расписания
        table_group = self.create_styled_group("Расписание занятий")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.schedule_table = self.create_table([
            "ID", "Дисциплина", "Группа", "Преподаватель", "Аудитория", "День", "Время", "Тип недели", "Действия"
        ])
        self.schedule_table.cellDoubleClicked.connect(self.on_schedule_action)
        table_layout.addWidget(self.schedule_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def load_groups(self):
        """Загрузка групп для фильтра"""
        query = "SELECT id, name FROM groups ORDER BY name"
        result = db.execute_query(query)
        if result:
            for group_id, group_name in result:
                self.group_filter.addItem(group_name, group_id)

    def load_students(self):
        """
        Студенты фильтруются по кафедре через связь:
        student → group → study_program → disciplines (учебный план) → department
        Но проще: студенты в группах, которые обучаются по дисциплинам кафедры.
        Однако в текущей схеме нет прямой связи group → department.
        Поэтому фильтрация студентов по кафедре — косвенная.

        Вариант: показывать всех студентов, чьи группы есть в учебных планах кафедры.
        """
        role = user_manager.current_user['role']
        dept_id = user_manager.current_user.get('department_id')

        if role == 'kafedra' and not dept_id:
            QMessageBox.warning(self, "Ошибка", "Не указана кафедра пользователя")
            return

        if role == 'kafedra':
            query = """
            SELECT DISTINCT s.id, s.fio, s.record_book_id, g.name,
                   CASE WHEN s.status THEN 'Активен' ELSE 'Отчислен' END
            FROM students s
            JOIN groups g ON s.group_id = g.id
            JOIN study_plans sp ON sp.group_id = g.id
            JOIN disciplines d ON sp.discipline_id = d.id
            WHERE d.department_id = %s
            ORDER BY g.name, s.fio
            """
            result = db.execute_query(query, (dept_id,))
        else:  # admin
            query = """
            SELECT s.id, s.fio, s.record_book_id, g.name,
                   CASE WHEN s.status THEN 'Активен' ELSE 'Отчислен' END
            FROM students s
            JOIN groups g ON s.group_id = g.id
            ORDER BY g.name, s.fio
            """
            result = db.execute_query(query)

        if result:
            table_data = [row + ("✏️",) for row in result]
            self.populate_table(self.students_table, table_data)
        else:
            self.students_table.setRowCount(1)
            self.students_table.setItem(0, 0, QTableWidgetItem("Нет данных"))

    def load_teachers(self):
        role = user_manager.current_user['role']
        dept_id = user_manager.current_user.get('department_id')

        if role == 'kafedra' and not dept_id:
            QMessageBox.warning(self, "Ошибка", "Не указана кафедра пользователя")
            return

        if role == 'kafedra':
            query = """
            SELECT t.id, t.fio, t.position, t.academic_degree, d.name
            FROM teachers t
            JOIN departments d ON t.department_id = d.id
            WHERE t.department_id = %s
            ORDER BY t.fio
            """
            result = db.execute_query(query, (dept_id,))
        else:  # admin
            query = """
            SELECT t.id, t.fio, t.position, t.academic_degree, d.name
            FROM teachers t
            JOIN departments d ON t.department_id = d.id
            ORDER BY t.fio
            """
            result = db.execute_query(query)

        if result:
            table_data = [row + ("✏️ 🗑️",) for row in result]
            self.populate_table(self.teachers_table, table_data)
        else:
            self.teachers_table.setRowCount(1)
            self.teachers_table.setItem(0, 0, QTableWidgetItem("Нет данных"))

    def add_teacher(self):
        """Добавление нового преподавателя"""
        from widgets.editors import TeacherEditor
        editor = TeacherEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_teachers()

    def on_teacher_action(self, row, column):
        """Обработка действий с преподавателем"""
        if column == 5:  # Колонка "Действия"
            teacher_id = self.teachers_table.item(row, 0).text()
            teacher_fio = self.teachers_table.item(row, 1).text()
            position = self.teachers_table.item(row, 2).text()
            academic_degree = self.teachers_table.item(row, 3).text()
            department_name = self.teachers_table.item(row, 4).text()

            # Получаем department_id
            query = "SELECT id FROM departments WHERE name = %s"
            result = db.execute_query(query, (department_name,))
            department_id = result[0][0] if result else None

            teacher_data = (teacher_id, teacher_fio, position, academic_degree, department_id)

            from widgets.editors import TeacherEditor
            editor = TeacherEditor(teacher_data, parent=self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                self.load_teachers()


    def add_schedule(self):
        """Добавление нового занятия в расписание"""
        from widgets.editors import ScheduleEditor
        editor = ScheduleEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_schedule()

    def on_schedule_action(self, row, column):
        if column == 8:  # Колонка "Действия"
            schedule_id = int(self.schedule_table.item(row, 0).text())
            discipline_name = self.schedule_table.item(row, 1).text()
            group_name = self.schedule_table.item(row, 2).text()
            teacher_name = self.schedule_table.item(row, 3).text()
            classroom_num = self.schedule_table.item(row, 4).text()
            start_time = self.schedule_table.item(row, 6).text().split('-')[0]
            end_time = self.schedule_table.item(row, 6).text().split('-')[1]
            week_type = self.schedule_table.item(row, 7).text()

            disc_id = self._get_discipline_id_by_name(discipline_name)
            group_id = self._get_group_id_by_name(group_name)
            teacher_id = self._get_teacher_id_by_name(teacher_name)
            class_id = self._get_classroom_id_by_number(classroom_num)

            if any(x is None for x in [disc_id, group_id, class_id]):
                QMessageBox.warning(self, "Ошибка", "Не удалось определить ID сущностей")
                return

            schedule_data = (schedule_id, disc_id, class_id, teacher_id, group_id, start_time, end_time, week_type)

            action = QMessageBox.question(
                self, "Действие",
                "Выберите действие:\n✅ — Редактировать\n🗑️ — Удалить",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if action == QMessageBox.StandardButton.Yes:
                from widgets.editors import ScheduleEditor
                editor = ScheduleEditor(schedule_data=schedule_data, parent=self)
                if editor.exec() == QDialog.DialogCode.Accepted:
                    self.load_schedule()
            elif action == QMessageBox.StandardButton.No:
                reply = QMessageBox.warning(
                    self, "Подтверждение",
                    f"Удалить занятие?\n{discipline_name}\nГруппа: {group_name}\nАудитория: {classroom_num}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    db.execute_query("DELETE FROM schedule WHERE id = %s", (schedule_id,), fetch=False)
                    self.load_schedule()

    def load_study_plans(self):
        role = user_manager.current_user['role']
        dept_id = user_manager.current_user.get('department_id')

        if role == 'kafedra' and not dept_id:
            QMessageBox.warning(self, "Ошибка", "Не указана кафедра пользователя")
            return

        if role == 'kafedra':
            query = """
            SELECT sp.id, d.name, g.name, t.fio, sp.semester, sp.hours_lecture, sp.hours_practice
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            WHERE d.department_id = %s
            ORDER BY g.name, sp.semester, d.name
            """
            result = db.execute_query(query, (dept_id,))
        else:  # admin
            query = """
            SELECT sp.id, d.name, g.name, t.fio, sp.semester, sp.hours_lecture, sp.hours_practice
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            ORDER BY g.name, sp.semester, d.name
            """
            result = db.execute_query(query)

        if result:
            table_data = [row + ("✏️ 🗑️",) for row in result]
            self.populate_table(self.plans_table, table_data)
        else:
            self.plans_table.setRowCount(1)
            self.plans_table.setItem(0, 0, QTableWidgetItem("Нет данных"))

    def load_schedule(self):
        role = user_manager.current_user['role']
        dept_id = user_manager.current_user.get('department_id')

        if role == 'kafedra' and not dept_id:
            QMessageBox.warning(self, "Ошибка", "Не указана кафедра пользователя")
            return

        if role == 'kafedra':
            query = """
            SELECT s.id, d.name, g.name, t.fio, c.number,
                   TO_CHAR(s.start_time, 'Day') as day_of_week,
                   CONCAT(TO_CHAR(s.start_time, 'HH24:MI'), '-', TO_CHAR(s.end_time, 'HH24:MI')) as time_range,
                   s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            JOIN groups g ON s.group_id = g.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            JOIN classrooms c ON s.classroom_id = c.id
            WHERE d.department_id = %s
            ORDER BY s.start_time, g.name
            """
            result = db.execute_query(query, (dept_id,))
        else:  # admin
            query = """
            SELECT s.id, d.name, g.name, t.fio, c.number,
                   TO_CHAR(s.start_time, 'Day') as day_of_week,
                   CONCAT(TO_CHAR(s.start_time, 'HH24:MI'), '-', TO_CHAR(s.end_time, 'HH24:MI')) as time_range,
                   s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            JOIN groups g ON s.group_id = g.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            JOIN classrooms c ON s.classroom_id = c.id
            ORDER BY s.start_time, g.name
            """
            result = db.execute_query(query)

        if result:
            table_data = []
            for row in result:
                table_data.append((
                    row[0],  # ID
                    row[1],  # Дисциплина
                    row[2],  # Группа
                    row[3] if row[3] else "Не назначен",  # Преподаватель
                    row[4],  # Аудитория
                    row[5].strip(),  # День недели
                    row[6],  # Время
                    row[7],  # Тип недели
                    "✏️ 🗑️"
                ))
            self.populate_table(self.schedule_table, table_data)
        else:
            self.schedule_table.setRowCount(1)
            self.schedule_table.setItem(0, 0, QTableWidgetItem("Нет данных"))

    def _get_discipline_id_by_name(self, name):
        res = db.execute_query("SELECT id FROM disciplines WHERE name = %s", (name,))
        return res[0][0] if res else None

    def _get_group_id_by_name(self, name):
        res = db.execute_query("SELECT id FROM groups WHERE name = %s", (name,))
        return res[0][0] if res else None

    def _get_teacher_id_by_name(self, name):
        if name == "Не назначен":
            return None
        res = db.execute_query("SELECT id FROM teachers WHERE fio = %s", (name,))
        return res[0][0] if res else None

    def _get_classroom_id_by_number(self, number):
        res = db.execute_query("SELECT id FROM classrooms WHERE number = %s", (number,))
        return res[0][0] if res else None

    def create_students_tab(self):
        """Вкладка управления студентами"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Панель управления
        control_group = self.create_styled_group("Управление студентами")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 25, 20, 20)

        self.group_filter = QComboBox()
        self.group_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
            }
        """)
        self.group_filter.addItem("Все группы", None)

        add_student_btn = self.create_styled_button("➕ Добавить студента")
        refresh_btn = self.create_styled_button("🔄 Обновить")

        add_student_btn.clicked.connect(self.add_student)
        refresh_btn.clicked.connect(self.load_students)
        self.group_filter.currentIndexChanged.connect(self.load_students)

        control_layout.addWidget(QLabel("👥 Группа:"))
        control_layout.addWidget(self.group_filter)
        control_layout.addWidget(add_student_btn)
        control_layout.addStretch()
        control_layout.addWidget(refresh_btn)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Таблица студентов
        table_group = self.create_styled_group("Список студентов")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.students_table = self.create_table([
            "ID", "ФИО", "Зачётная книжка", "Группа", "Статус", "Действия"
        ])
        self.students_table.cellDoubleClicked.connect(self.edit_student)
        table_layout.addWidget(self.students_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def add_student(self):
        """Добавление нового студента"""
        from widgets.editors import StudentEditor
        editor = StudentEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_students()

    def edit_student(self, row, column):
        """Редактирование студента"""
        try:
            if column == 5:  # Колонка "Действия"
                # Получаем данные из таблицы
                student_id_item = self.students_table.item(row, 0)
                student_fio_item = self.students_table.item(row, 1)
                record_book_item = self.students_table.item(row, 2)
                group_name_item = self.students_table.item(row, 3)
                status_item = self.students_table.item(row, 4)

                if not all([student_id_item, student_fio_item, record_book_item, group_name_item, status_item]):
                    QMessageBox.warning(self, "Ошибка", "Не удалось получить данные студента")
                    return

                student_id = student_id_item.text()
                student_fio = student_fio_item.text()
                record_book = record_book_item.text()
                group_name = group_name_item.text()
                status = status_item.text() == "Активен"

                # Получаем group_id по имени группы
                query = "SELECT id FROM groups WHERE name = %s"
                result = db.execute_query(query, (group_name,))
                if not result:
                    QMessageBox.warning(self, "Ошибка", "Не удалось найти группу")
                    return

                group_id = result[0][0]

                student_data = (student_id, student_fio, record_book, status, group_id)

                from widgets.editors import StudentEditor
                editor = StudentEditor(student_data, parent=self)
                if editor.exec() == QDialog.DialogCode.Accepted:
                    self.load_students()
        except Exception as e:
            print(f"Ошибка при редактировании студента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании студента: {str(e)}")

    def create_reports_tab(self):
        """Вкладка отчетов для сотрудника кафедры"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Группа для генерации отчетов
        reports_group = self.create_styled_group("Генерация отчетов")
        reports_layout = QVBoxLayout()
        reports_layout.setContentsMargins(25, 25, 25, 25)
        reports_layout.setSpacing(15)

        # Кнопки отчетов
        grades_report_btn = self.create_styled_button("📊 Ведомость успеваемости")
        student_rating_btn = self.create_styled_button("🏆 Рейтинг студентов")
        classroom_occupancy_btn = self.create_styled_button("🏫 Занятость аудиторий")

        grades_report_btn.clicked.connect(self.generate_grades_report)
        student_rating_btn.clicked.connect(self.generate_student_rating)
        classroom_occupancy_btn.clicked.connect(self.generate_classroom_occupancy)

        reports_layout.addWidget(grades_report_btn)
        reports_layout.addWidget(student_rating_btn)
        reports_layout.addWidget(classroom_occupancy_btn)

        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        # Информация об отчетах
        info_group = self.create_styled_group("Информация")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "• Ведомость успеваемости - отчет по оценкам студентов\n"
            "• Рейтинг студентов - академический рейтинг по успеваемости\n"
            "• Занятость аудиторий - отчет по использованию учебных помещений"
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px; line-height: 1.6;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        widget.setLayout(layout)
        return widget


    def generate_grades_report(self):
        """Генерация ведомости успеваемости"""
        from widgets.report_dialogs import GradesReportDialog
        dialog = GradesReportDialog(self)
        dialog.exec()

    def generate_student_rating(self):
        """Генерация рейтинга студентов"""
        from widgets.report_dialogs import StudentRatingDialog
        dialog = StudentRatingDialog(self)
        dialog.exec()

    def generate_classroom_occupancy(self):
        """Генерация отчета по занятости аудиторий - упрощенная версия"""
        try:
            print("🔄 ЗАПУСК ГЕНЕРАЦИИ ОТЧЕТА")

            # Создаем и сохраняем прогресс-диалог
            self._progress = QProgressDialog(
                "Генерация отчета по занятости аудиторий...",
                "Отмена", 0, 0, self
            )
            self._progress.setWindowTitle("Пожалуйста, подождите")
            self._progress.setWindowModality(Qt.WindowModality.WindowModal)
            self._progress.setFixedSize(400, 120)
            self._progress.show()

            # Запускаем в основном потоке с небольшой задержкой
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self._generate_directly)

        except Exception as e:
            print(f"💥 Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить генерацию: {str(e)}")

    def _generate_directly(self):
        """Прямая генерация в основном потоке"""
        try:
            from services.report_service import DocumentGenerator

            print("🎯 Начинаем генерацию отчета...")
            file_path = DocumentGenerator.generate_classroom_occupancy_report()

            # Закрываем прогресс-диалог
            if hasattr(self, '_progress'):
                self._progress.close()
                del self._progress

            if file_path:
                print(f"✅ Отчет создан: {file_path}")
                reply = QMessageBox.question(
                    self,
                    "✅ Отчет сгенерирован",
                    "Отчет по занятости аудиторий успешно сгенерирован. Хотите открыть файл?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_file(file_path)
            else:
                QMessageBox.critical(self, "❌ Ошибка", "Не удалось сгенерировать отчет")

        except Exception as e:
            if hasattr(self, '_progress'):
                self._progress.close()
                del self._progress

            print(f"💥 Ошибка при генерации: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{str(e)}")

    def on_report_generated(self, file_path, progress, report_name):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "Отчет сгенерирован",
            f"{report_name} успешно сгенерирован. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать отчет: {error}")

    def open_file(self, file_path):
        """Открытие сгенерированного файла"""
        try:
            import os
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.information(
                self,
                "Файл сохранен",
                f"Файл сохранен по пути: {file_path}\n\nОшибка при открытии: {str(e)}"
            )


class TeacherPanel(BasePanel):
    """Панель преподавателя"""

    def __init__(self, teacher_id):
        print(f"🎯 ВХОД В TeacherPanel.__init__ с teacher_id: {teacher_id}")
        self.teacher_id = teacher_id
        print(f"✅ teacher_id установлен: {self.teacher_id}")
        super().__init__()
        print(f"✅ TeacherPanel.__init__ завершен")

    def setup_ui(self):
        super().setup_ui()

        # Заголовок
        title = QLabel("Панель преподавателя")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 10px;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)

        # Мои дисциплины
        disciplines_tab = self.create_disciplines_tab()
        tabs.addTab(disciplines_tab, "📚 Мои дисциплины")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Моё расписание")

        # Успеваемость
        grades_tab = self.create_grades_tab()
        tabs.addTab(grades_tab, "🎯 Успеваемость")

        # Нагрузка
        workload_tab = self.create_workload_tab()
        tabs.addTab(workload_tab, "📈 Нагрузка")

        # Отчеты
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def load_initial_data(self):
        """Загрузка начальных данных"""
        try:
            print(f"Загрузка данных для преподавателя ID: {self.teacher_id}")
            self.load_teacher_disciplines()
            self.load_teacher_schedule()
            self.load_workload()
            self.load_disciplines_for_grading()
        except Exception as e:
            print(f"Ошибка при загрузке данных преподавателя: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def create_disciplines_tab(self):
        """Вкладка моих дисциплин"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Мои дисциплины")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображаются дисциплины, которые вы ведёте.\n"
            "Здесь можно просмотреть информацию о группах, семестрах и распределении часов."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить список")
        refresh_btn.clicked.connect(self.load_teacher_disciplines)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица дисциплин
        table_group = self.create_styled_group("Список дисциплин")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.disciplines_table = self.create_table([
            "Дисциплина", "Группа", "Семестр", "Часы (лек/пр)"
        ])
        table_layout.addWidget(self.disciplines_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        """Вкладка моего расписания"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Моё расписание")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображается ваше расписание занятий.\n"
            "Здесь можно просмотреть время, аудитории и группы для ваших занятий."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить расписание")
        refresh_btn.clicked.connect(self.load_teacher_schedule)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица расписания
        table_group = self.create_styled_group("Расписание занятий")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.schedule_table = self.create_table([
            "День", "Время", "Дисциплина", "Группа", "Аудитория", "Тип недели"
        ])
        table_layout.addWidget(self.schedule_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_workload_tab(self):
        """Вкладка нагрузки преподавателя"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Статистика нагрузки
        stats_group = self.create_styled_group("Статистика нагрузки")
        stats_layout = QFormLayout()
        stats_layout.setContentsMargins(25, 25, 25, 25)
        stats_layout.setSpacing(15)

        self.total_hours_label = QLabel("0")
        self.lecture_hours_label = QLabel("0")
        self.practice_hours_label = QLabel("0")
        self.groups_count_label = QLabel("0")

        # Стили для меток статистики
        stats_style = """
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
        """
        self.total_hours_label.setStyleSheet(stats_style)
        self.lecture_hours_label.setStyleSheet(stats_style)
        self.practice_hours_label.setStyleSheet(stats_style)
        self.groups_count_label.setStyleSheet(stats_style)

        stats_layout.addRow("🕐 Общее количество часов:", self.total_hours_label)
        stats_layout.addRow("📚 Лекционные часы:", self.lecture_hours_label)
        stats_layout.addRow("💻 Практические часы:", self.practice_hours_label)
        stats_layout.addRow("👥 Количество групп:", self.groups_count_label)

        refresh_btn = self.create_styled_button("🔄 Обновить статистику")
        refresh_btn.clicked.connect(self.load_workload)
        stats_layout.addRow("", refresh_btn)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Детальная таблица нагрузки
        table_group = self.create_styled_group("Детальная нагрузка")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.workload_table = self.create_table([
            "Дисциплина", "Группа", "Лекции (ч)", "Практика (ч)", "Всего (ч)"
        ])
        table_layout.addWidget(self.workload_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def load_teacher_disciplines(self):
        """Загрузка дисциплин преподавателя"""
        try:
            query = """
            SELECT d.name, g.name, sp.semester, 
                   CONCAT(sp.hours_lecture, '/', sp.hours_practice)
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s
            ORDER BY g.name, sp.semester
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.populate_table(self.disciplines_table, result)
            else:
                self.disciplines_table.setRowCount(0)
                # Добавляем сообщение об отсутствии данных
                self.disciplines_table.setRowCount(1)
                self.disciplines_table.setItem(0, 0, QTableWidgetItem("Нет данных о дисциплинах"))
        except Exception as e:
            print(f"Ошибка при загрузке дисциплин: {e}")
            self.disciplines_table.setRowCount(1)
            self.disciplines_table.setItem(0, 0, QTableWidgetItem("Ошибка загрузки данных"))

    def load_teacher_schedule(self):
        """Загрузка расписания преподавателя"""
        try:
            query = """
            SELECT 
                TO_CHAR(s.start_time, 'Day') as day,
                CONCAT(TO_CHAR(s.start_time, 'HH24:MI'), '-', TO_CHAR(s.end_time, 'HH24:MI')) as time,
                d.name as discipline,
                g.name as group_name,
                c.number as classroom,
                s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            JOIN groups g ON s.group_id = g.id
            JOIN classrooms c ON s.classroom_id = c.id
            WHERE s.teacher_id = %s
            ORDER BY s.start_time
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.populate_table(self.schedule_table, result)
            else:
                self.schedule_table.setRowCount(0)
                self.schedule_table.setRowCount(1)
                self.schedule_table.setItem(0, 0, QTableWidgetItem("Нет данных о расписании"))
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")
            self.schedule_table.setRowCount(1)
            self.schedule_table.setItem(0, 0, QTableWidgetItem("Ошибка загрузки данных"))

    def load_workload(self):
        """Загрузка нагрузки преподавателя"""
        try:
            # Общая статистика
            query = """
            SELECT COALESCE(SUM(hours_lecture + hours_practice), 0),
                   COALESCE(SUM(hours_lecture), 0),
                   COALESCE(SUM(hours_practice), 0),
                   COUNT(DISTINCT group_id)
            FROM study_plans
            WHERE teacher_id = %s
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                total, lecture, practice, groups = result[0]
                self.total_hours_label.setText(str(total))
                self.lecture_hours_label.setText(str(lecture))
                self.practice_hours_label.setText(str(practice))
                self.groups_count_label.setText(str(groups))

            # Детальная нагрузка
            detail_query = """
            SELECT d.name, g.name, sp.hours_lecture, sp.hours_practice,
                   (sp.hours_lecture + sp.hours_practice)
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s
            ORDER BY g.name, d.name
            """
            detail_result = db.execute_query(detail_query, (self.teacher_id,))
            if detail_result:
                self.populate_table(self.workload_table, detail_result)
            else:
                self.workload_table.setRowCount(0)

        except Exception as e:
            print(f"Ошибка при загрузке нагрузки: {e}")

    def create_grades_tab(self):
        """Вкладка управления успеваемостью"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Группа фильтров
        filter_group = self.create_styled_group("Фильтры для выставления оценок")
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(20, 25, 20, 20)

        self.grade_discipline_filter = QComboBox()
        self.grade_group_filter = QComboBox()

        self.grade_discipline_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
            }
        """)
        self.grade_group_filter.setStyleSheet("""
            QComboBox {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
            }
        """)

        self.grade_discipline_filter.currentIndexChanged.connect(self.on_discipline_changed)

        filter_layout.addWidget(QLabel("📚 Дисциплина:"))
        filter_layout.addWidget(self.grade_discipline_filter)
        filter_layout.addWidget(QLabel("👥 Группа:"))
        filter_layout.addWidget(self.grade_group_filter)
        filter_layout.addStretch()

        load_btn = self.create_styled_button("🔄 Загрузить студентов")
        load_btn.clicked.connect(self.load_students_for_grading)

        filter_layout.addWidget(load_btn)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Таблица студентов для выставления оценок
        table_group = self.create_styled_group("Студенты для оценки")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.grades_table = self.create_table([
            "ID", "Студент", "Зачётная книжка", "Текущая оценка", "Действия"
        ])
        self.grades_table.cellDoubleClicked.connect(self.edit_grade)
        table_layout.addWidget(self.grades_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Загружаем дисциплины при инициализации
        self.load_disciplines_for_grading()

        widget.setLayout(layout)
        return widget

    def load_students_for_grading(self):
        """Загрузка студентов для выставления оценок"""
        try:
            discipline_id = self.grade_discipline_filter.currentData()
            group_id = self.grade_group_filter.currentData()

            if not discipline_id:
                QMessageBox.warning(self, "Ошибка", "Выберите дисциплину")
                return

            # Получаем study_plan_id
            study_plan_query = """
            SELECT id FROM study_plans 
            WHERE discipline_id = %s AND teacher_id = %s AND (%s IS NULL OR group_id = %s)
            """
            study_plan_result = db.execute_query(study_plan_query, (discipline_id, self.teacher_id, group_id, group_id))

            if not study_plan_result:
                QMessageBox.information(self, "Информация", "Нет учебного плана для выбранных параметров")
                self.grades_table.setRowCount(0)
                return

            study_plan_id = study_plan_result[0][0]

            query = """
            SELECT s.id, s.fio, s.record_book_id, 
                   COALESCE(g.grade, 'Нет оценки') as current_grade,
                   COALESCE(g.id, NULL) as grade_id
            FROM students s
            JOIN groups gr ON s.group_id = gr.id
            JOIN study_plans sp ON sp.group_id = gr.id AND sp.discipline_id = %s AND sp.teacher_id = %s
            LEFT JOIN grades g ON g.student_id = s.id AND g.study_plan_id = sp.id
            WHERE (%s IS NULL OR s.group_id = %s) AND s.status = true
            ORDER BY s.fio
            """
            result = db.execute_query(query, (discipline_id, self.teacher_id, group_id, group_id))

            if result:
                # Добавляем кнопки действий
                table_data = []
                for row in result:
                    student_id, fio, record_book, grade, grade_id = row
                    if grade == 'Нет оценки':
                        actions = "➕ Выставить"
                    else:
                        actions = "✏️ Редактировать | 🗑️ Удалить"
                    table_data.append((student_id, fio, record_book, grade, actions))

                self.populate_table(self.grades_table, table_data)
            else:
                self.grades_table.setRowCount(0)
                QMessageBox.information(self, "Информация", "Нет студентов для выбранных параметров")

        except Exception as e:
            print(f"Ошибка при загрузке студентов: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить студентов: {str(e)}")

    def edit_grade(self, row, column):
        """Редактирование или удаление оценки студента"""
        if column == 4:  # Колонка "Действия"
            student_id = self.grades_table.item(row, 0).text()
            student_fio = self.grades_table.item(row, 1).text()
            record_book = self.grades_table.item(row, 2).text()
            current_grade = self.grades_table.item(row, 3).text()

            student_data = (student_id, student_fio, record_book)

            # Получаем study_plan_id
            discipline_id = self.grade_discipline_filter.currentData()
            group_id = self.grade_group_filter.currentData()

            study_plan_query = """
            SELECT id FROM study_plans 
            WHERE discipline_id = %s AND group_id = %s AND teacher_id = %s
            """
            study_plan_result = db.execute_query(study_plan_query, (discipline_id, group_id, self.teacher_id))

            if not study_plan_result:
                QMessageBox.warning(self, "Ошибка", "Не найден учебный план")
                return

            study_plan_id = study_plan_result[0][0]

            # Проверяем есть ли существующая оценка
            existing_grade_query = """
            SELECT id, student_id, grade, type, exam_date 
            FROM grades 
            WHERE student_id = %s AND study_plan_id = %s
            """
            existing_grade_result = db.execute_query(existing_grade_query, (student_id, study_plan_id))

            existing_grade = existing_grade_result[0] if existing_grade_result else None

            if current_grade == 'Нет оценки':
                # Выставление новой оценки
                from widgets.editors import GradeEditor
                editor = GradeEditor(student_data, study_plan_id, None, parent=self)
                if editor.exec() == QDialog.DialogCode.Accepted:
                    self.load_students_for_grading()
            else:
                # Редактирование или удаление существующей оценки
                self.show_grade_actions_dialog(student_id, student_fio, existing_grade, study_plan_id)

    def show_grade_actions_dialog(self, student_id, student_fio, existing_grade, study_plan_id):
        """Диалог выбора действия с оценкой"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Действия с оценкой: {student_fio}")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout()

        info_label = QLabel(f"Студент: {student_fio}\nТекущая оценка: {existing_grade[2]}")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(info_label)

        edit_btn = QPushButton("✏️ Редактировать оценку")
        delete_btn = QPushButton("🗑️ Удалить оценку")
        cancel_btn = QPushButton("Отмена")

        edit_btn.clicked.connect(lambda: self.edit_existing_grade(existing_grade, student_fio, dialog))
        delete_btn.clicked.connect(lambda: self.delete_grade(existing_grade[0], student_fio, dialog))
        cancel_btn.clicked.connect(dialog.reject)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(cancel_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def edit_existing_grade(self, existing_grade, student_fio, parent_dialog):
        """Редактирование существующей оценки"""
        student_data = (existing_grade[1], student_fio, "")
        from widgets.editors import GradeEditor
        editor = GradeEditor(student_data, None, existing_grade, parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            parent_dialog.accept()
            self.load_students_for_grading()

    def delete_grade(self, grade_id, student_fio, parent_dialog):
        """Удаление оценки"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить оценку у студента {student_fio}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM grades WHERE id = %s"
                success = db.execute_query(query, (grade_id,), fetch=False)

                if success:
                    QMessageBox.information(self, "Успех", "Оценка удалена")
                    parent_dialog.accept()
                    self.load_students_for_grading()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить оценку")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении оценки: {str(e)}")

    def create_reports_tab(self):
        """Вкладка отчетов для преподавателя"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Группа для генерации отчетов
        reports_group = self.create_styled_group("Генерация отчетов")
        reports_layout = QVBoxLayout()
        reports_layout.setContentsMargins(25, 25, 25, 25)
        reports_layout.setSpacing(15)

        # Кнопки отчетов
        workload_report_btn = self.create_styled_button("📊 Отчет по нагрузке", "#27ae60")
        workload_report_btn.clicked.connect(self.generate_workload_report)

        reports_layout.addWidget(workload_report_btn)
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        # Информация об отчетах
        info_group = self.create_styled_group("Информация")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "• Отчет по нагрузке - детальная информация о вашей учебной нагрузке\n"
            "  по дисциплинам и группам с распределением часов"
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px; line-height: 1.6;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        widget.setLayout(layout)
        return widget

    def generate_workload_report(self):
        """Генерация отчета по нагрузке"""
        try:
            print(f"🔍 Генерация отчета по нагрузке для teacher_id: {self.teacher_id}")

            if not hasattr(self, 'teacher_id') or not self.teacher_id:
                QMessageBox.warning(self, "Ошибка", "ID преподавателя не найден")
                return

            progress = QProgressDialog("Генерация отчета по нагрузке...", "Отмена", 0, 0, self)
            progress.setWindowTitle("Пожалуйста, подождите")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setStyleSheet("""
                QProgressDialog {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            progress.show()

            # Запуск в отдельном потоке
            self.thread = ReportGenerationThread('workload_report', teacher_id=self.teacher_id)
            self.thread.finished.connect(lambda path: self.on_report_generated(path, progress, "Отчет по нагрузке"))
            self.thread.error.connect(lambda error: self.on_report_error(error, progress))
            self.thread.start()

        except Exception as e:
            print(f"💥 Ошибка при запуске генерации отчета: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить генерацию отчета: {e}")

    def on_report_generated(self, file_path, progress, report_name):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "✅ Отчет сгенерирован",
            f"{report_name} успешно сгенерирован. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        print(f"💥 Ошибка генерации отчета: {error}")
        QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{error}")

    def open_file(self, file_path):
        """Открытие сгенерированного файла"""
        try:
            import os
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.information(
                self,
                "📁 Файл сохранен",
                f"Файл сохранен по пути: {file_path}\n\nОшибка при открытии: {str(e)}"
            )


    def load_disciplines_for_grading(self):
        """Загрузка дисциплин преподавателя для выставления оценок"""
        try:
            query = """
               SELECT DISTINCT d.id, d.name
               FROM study_plans sp
               JOIN disciplines d ON sp.discipline_id = d.id
               WHERE sp.teacher_id = %s
               ORDER BY d.name
               """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.grade_discipline_filter.clear()
                self.grade_discipline_filter.addItem("Выберите дисциплину", None)
                for discipline_id, discipline_name in result:
                    self.grade_discipline_filter.addItem(discipline_name, discipline_id)
            else:
                print("Нет дисциплин для преподавателя")
        except Exception as e:
            print(f"Ошибка при загрузке дисциплин: {e}")

    def load_groups_for_grading(self):
        """Загрузка групп для выбранной дисциплины"""
        try:
            discipline_id = self.grade_discipline_filter.currentData()
            if not discipline_id:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Сначала выберите дисциплину", None)
                return

            query = """
            SELECT DISTINCT g.id, g.name
            FROM study_plans sp
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s AND sp.discipline_id = %s
            ORDER BY g.name
            """
            result = db.execute_query(query, (self.teacher_id, discipline_id))
            if result:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Все группы", None)
                for group_id, group_name in result:
                    self.grade_group_filter.addItem(group_name, group_id)
            else:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Нет групп для этой дисциплины", None)
        except Exception as e:
            print(f"Ошибка при загрузке групп: {e}")

    def on_discipline_changed(self):
        """Обработчик изменения выбранной дисциплины"""
        self.load_groups_for_grading()
        # Очищаем таблицу студентов при смене дисциплины
        self.grades_table.setRowCount(0)


class StudentPanel(BasePanel):
    """Панель студента"""

    def __init__(self, student_id):
        self.student_id = student_id  # Сначала устанавливаем student_id
        print(f"Создана StudentPanel с student_id: {student_id}")
        super().__init__()  # Затем вызываем родительский конструктор

    def setup_ui(self):
        super().setup_ui()

        # Заголовок
        title = QLabel("Панель студента")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 10px;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)

        # Успеваемость
        grades_tab = self.create_grades_tab()
        tabs.addTab(grades_tab, "📖 Успеваемость")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Расписание")

        # Зачётная книжка
        record_book_tab = self.create_record_book_tab()
        tabs.addTab(record_book_tab, "📚 Зачётная книжка")

        # Отчеты
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_student_grades()
        self.load_student_schedule()
        self.load_record_book()

    def create_grades_tab(self):
        """Вкладка успеваемости"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Успеваемость")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображаются ваши текущие оценки по дисциплинам.\n"
            "Здесь можно просмотреть оценки, типы контроля и даты экзаменов."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить оценки")
        refresh_btn.clicked.connect(self.load_student_grades)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица оценок
        table_group = self.create_styled_group("Текущие оценки")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.grades_table = self.create_table([
            "Дисциплина", "Оценка", "Тип контроля", "Дата", "Преподаватель"
        ])
        table_layout.addWidget(self.grades_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Статистика успеваемости
        stats_group = self.create_styled_group("Статистика успеваемости")
        stats_layout = QFormLayout()
        stats_layout.setContentsMargins(25, 25, 25, 25)
        stats_layout.setSpacing(15)

        self.avg_grade_label = QLabel("0.0")
        self.total_subjects_label = QLabel("0")
        self.completed_label = QLabel("0")

        # Стили для меток статистики
        stats_style = """
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
            }
        """
        self.avg_grade_label.setStyleSheet(stats_style)
        self.total_subjects_label.setStyleSheet(stats_style)
        self.completed_label.setStyleSheet(stats_style)

        stats_layout.addRow("📊 Средний балл:", self.avg_grade_label)
        stats_layout.addRow("📚 Всего дисциплин:", self.total_subjects_label)
        stats_layout.addRow("✅ Сдано дисциплин:", self.completed_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        """Вкладка расписания"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Расписание занятий")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображается ваше расписание занятий.\n"
            "Здесь можно просмотреть время, дисциплины, преподавателей и аудитории."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить расписание")
        refresh_btn.clicked.connect(self.load_student_schedule)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица расписания
        table_group = self.create_styled_group("Расписание")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.schedule_table = self.create_table([
            "День", "Время", "Дисциплина", "Преподаватель", "Аудитория", "Тип недели"
        ])
        table_layout.addWidget(self.schedule_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def create_record_book_tab(self):
        """Вкладка зачётной книжки"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Информационная группа
        info_group = self.create_styled_group("Зачётная книжка")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "В этой вкладке отображается полная история вашей успеваемости.\n"
            "Здесь можно просмотреть все оценки по семестрам в формате зачётной книжки."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px; line-height: 1.4;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        refresh_btn = self.create_styled_button("🔄 Обновить данные")
        refresh_btn.clicked.connect(self.load_record_book)
        info_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Таблица зачётной книжки
        table_group = self.create_styled_group("История успеваемости")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 25, 15, 15)

        self.record_book_table = self.create_table([
            "Семестр", "Дисциплина", "Оценка", "Тип", "Дата", "Преподаватель"
        ])
        table_layout.addWidget(self.record_book_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        widget.setLayout(layout)
        return widget

    def load_student_grades(self):
        """Загрузка оценок студента"""
        try:
            print(f"Загрузка оценок для студента ID: {self.student_id}")
            query = """
            SELECT d.name, g.grade, g.type, g.exam_date, t.fio
            FROM grades g
            JOIN study_plans sp ON g.study_plan_id = sp.id
            JOIN disciplines d ON sp.discipline_id = d.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            WHERE g.student_id = %s
            ORDER BY g.exam_date DESC
            """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.grades_table, result)

                # Расчет статистики
                numeric_grades = []
                completed_count = 0
                for row in result:
                    grade = row[1]
                    if grade and grade.isdigit():
                        numeric_grades.append(int(grade))
                    if grade and grade in ['зачёт', '5', '4', '3']:
                        completed_count += 1

                if numeric_grades:
                    avg_grade = sum(numeric_grades) / len(numeric_grades)
                    self.avg_grade_label.setText(f"{avg_grade:.2f}")
                else:
                    self.avg_grade_label.setText("0.0")

                self.total_subjects_label.setText(str(len(set([r[0] for r in result]))))
                self.completed_label.setText(str(completed_count))
            else:
                print("Нет данных об оценках")
                self.grades_table.setRowCount(0)
                self.avg_grade_label.setText("0.0")
                self.total_subjects_label.setText("0")
                self.completed_label.setText("0")

        except Exception as e:
            print(f"Ошибка при загрузке оценок: {e}")
            self.grades_table.setRowCount(0)

    def load_student_schedule(self):
        """Загрузка расписания студента"""
        try:
            print(f"Загрузка расписания для студента ID: {self.student_id}")
            query = """
            SELECT 
                TO_CHAR(s.start_time, 'Day') as day,
                CONCAT(TO_CHAR(s.start_time, 'HH24:MI'), '-', TO_CHAR(s.end_time, 'HH24:MI')) as time,
                d.name as discipline,
                t.fio as teacher,
                c.number as classroom,
                s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            JOIN classrooms c ON s.classroom_id = c.id
            JOIN groups g ON s.group_id = g.id
            JOIN students st ON st.group_id = g.id
            WHERE st.id = %s
            ORDER BY s.start_time
            """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.schedule_table, result)
            else:
                self.schedule_table.setRowCount(0)
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")
            self.schedule_table.setRowCount(0)

    def load_record_book(self):
        """Загрузка зачётной книжки"""
        try:
            print(f"Загрузка зачётной книжки для студента ID: {self.student_id}")
            query = """
            SELECT sp.semester, d.name, g.grade, g.type, g.exam_date, t.fio
            FROM grades g
            JOIN study_plans sp ON g.study_plan_id = sp.id
            JOIN disciplines d ON sp.discipline_id = d.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            WHERE g.student_id = %s
            ORDER BY sp.semester, d.name
            """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.record_book_table, result)
            else:
                self.record_book_table.setRowCount(0)
        except Exception as e:
            print(f"Ошибка при загрузке зачётной книжки: {e}")
            self.record_book_table.setRowCount(0)

    def create_reports_tab(self):
        """Вкладка отчетов для студента"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Группа для генерации отчетов
        reports_group = self.create_styled_group("Генерация отчетов")
        reports_layout = QVBoxLayout()
        reports_layout.setContentsMargins(25, 25, 25, 25)
        reports_layout.setSpacing(15)

        # Кнопки отчетов
        record_book_btn = self.create_styled_button("📚 Зачётная книжка", "#27ae60")
        record_book_btn.clicked.connect(self.generate_record_book)

        reports_layout.addWidget(record_book_btn)
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        # Информация об отчетах
        info_group = self.create_styled_group("Информация")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "• Зачётная книжка - официальный документ с полной историей\n"
            "  вашей успеваемости по всем семестрам обучения"
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px; line-height: 1.6;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        widget.setLayout(layout)
        return widget

    def generate_record_book(self):
        """Генерация зачётной книжки"""
        from widgets.report_dialogs import RecordBookDialog
        dialog = RecordBookDialog(self)
        # Автоматически выбираем текущего студента
        for i in range(dialog.student_combo.count()):
            if dialog.student_combo.itemData(i) == self.student_id:
                dialog.student_combo.setCurrentIndex(i)
                break
        dialog.exec()