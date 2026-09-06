from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QMessageBox,
                             QFrame, QSizePolicy, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from user_manager import user_manager
from widgets.role_panels import AdminPanel, DekanatPanel, TeacherPanel, StudentPanel


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_panel = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Учебная деятельность кафедры - Система управления')
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QFrame#sidebar {
                background-color: #2c3e50;
                border: none;
            }
            QLabel#user_info {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-bottom: 1px solid #34495e;
            }
            QPushButton#nav_button {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                text-align: left;
                padding: 12px 15px;
                font-size: 14px;
                margin: 2px 5px;
                border-radius: 5px;
            }
            QPushButton#nav_button:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton#nav_button:checked {
                background-color: #3498db;
                color: white;
            }
            QPushButton#logout_button {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin: 10px 5px;
            }
            QPushButton#logout_button:hover {
                background-color: #c0392b;
            }
            QFrame#content {
                background-color: white;
                border-radius: 10px;
                margin: 10px;
                border: 1px solid #e0e0e0;
            }
            QLabel#system_info {
                color: #bdc3c7;
                font-size: 11px;
                line-height: 1.3;
                padding: 10px;
                text-align: center;
            }
        """)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Сайдбар
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 1)

        # Область контента
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area, 4)

        central_widget.setLayout(main_layout)

        # Загружаем начальные данные
        self.load_initial_data()

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Информация о пользователе
        user_info = QLabel(f"{user_manager.current_user['fio']}\n"
                           f"Роль: {self.get_role_name(user_manager.current_user['role'])}")
        user_info.setObjectName("user_info")
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(user_info)

        # Навигационные кнопки (упрощенная версия - только информационные виджеты)
        nav_buttons = self.create_navigation_buttons()
        layout.addWidget(nav_buttons)

        # Растягивающийся элемент, чтобы прижать остальные элементы к верху
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        guide_btn = QPushButton("📖 Справка")
        guide_btn.setObjectName("nav_button")
        guide_btn.clicked.connect(self.show_user_guide)
        layout.addWidget(guide_btn)

        # Кнопка выхода
        logout_btn = QPushButton("Выйти из системы")
        logout_btn.setObjectName("logout_button")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        # Информация о системе (ПОД кнопкой выхода)
        system_info = self.create_system_info()
        layout.addWidget(system_info)

        sidebar.setLayout(layout)
        return sidebar

    def create_navigation_buttons(self):
        """Создание навигационных кнопок - упрощенная версия"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Только информационные виджеты, без функциональных кнопок
        info_group = QGroupBox("Навигация")
        info_layout = QVBoxLayout()

        # Информация о доступных разделах
        nav_info = QLabel(
            "Используйте вкладки в основной\n"
            "области для перехода между\n"
            "разделами системы"
        )
        nav_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_info.setWordWrap(True)
        nav_info.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 12px;
                line-height: 1.4;
                padding: 10px;
            }
        """)

        info_layout.addWidget(nav_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        widget.setLayout(layout)
        return widget

    def create_system_info(self):
        """Создание блока информации о системе"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)

        # Группа для информации о системе
        system_group = QGroupBox("О системе")
        system_group.setStyleSheet("""
            QGroupBox {
                color: #95a5a6;
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #34495e;
                border-radius: 5px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 5px 0 5px;
                color: #95a5a6;
            }
        """)

        system_layout = QVBoxLayout()
        system_layout.setContentsMargins(8, 15, 8, 8)

        # Информация о системе
        system_label = QLabel(
            "Академическая успеваемость\n"
            "Система учета академической успеваемости\n\n"
            "Версия: 1.0\n"
            "КубГТУ © 2026"
        )
        system_label.setObjectName("system_info")
        system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_label.setWordWrap(True)

        system_layout.addWidget(system_label)
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        widget.setLayout(layout)
        return widget

    def create_content_area(self):
        widget = QWidget()
        widget.setObjectName("content")

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Создаем stacked widget для переключения между панелями
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        widget.setLayout(self.content_layout)
        return widget

    def show_user_guide(self):
        from user_guide_window import UserGuideWindow
        role = user_manager.current_user['role']
        self.guide_window = UserGuideWindow(role, self)
        self.guide_window.show()

    def get_role_name(self, role):
        role_names = {
            'admin': 'Администратор',
            'dekanat': 'Сотрудник кафедры',
            'teacher': 'Преподаватель',
            'student': 'Студент'
        }
        return role_names.get(role, role)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        role = user_manager.current_user['role']
        print(f"=== НАЧАЛО ЗАГРУЗКИ ДАННЫХ ===")
        print(f"🎯 Роль из user_manager: '{role}'")

        try:
            if role == 'admin':
                self.admin_panel = AdminPanel()
                self.stacked_widget.addWidget(self.admin_panel)
                self.current_panel = self.admin_panel

            elif role == 'dekanat' or role == 'kafedra':
                self.dekanat_panel = DekanatPanel()
                self.stacked_widget.addWidget(self.dekanat_panel)
                self.current_panel = self.dekanat_panel

            elif role == 'teacher':
                teacher_id = user_manager.current_user.get('teacher_db_id') or user_manager.current_user.get(
                    'teacher_id')
                if teacher_id:
                    self.teacher_panel = TeacherPanel(teacher_id)
                    self.stacked_widget.addWidget(self.teacher_panel)
                    self.current_panel = self.teacher_panel
                else:
                    QMessageBox.warning(self, "Ошибка", "ID преподавателя не найден")

            elif role == 'student':
                student_id = user_manager.current_user.get('student_db_id') or user_manager.current_user.get(
                    'student_id')
                if student_id:
                    self.student_panel = StudentPanel(student_id)
                    self.stacked_widget.addWidget(self.student_panel)
                    self.current_panel = self.student_panel
                else:
                    QMessageBox.warning(self, "Ошибка", "ID студента не найден")

            # Устанавливаем текущую панель
            if self.current_panel:
                self.stacked_widget.setCurrentWidget(self.current_panel)
                # Загружаем данные после отображения
                QTimer.singleShot(100, self.load_panel_data)

        except Exception as e:
            print(f"💥 Ошибка при загрузке интерфейса: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить интерфейс: {str(e)}")

    def load_panel_data(self):
        """Загрузка данных для текущей панели"""
        try:
            if hasattr(self.current_panel, 'load_initial_data'):
                self.current_panel.load_initial_data()
        except Exception as e:
            print(f"Ошибка при загрузке данных панели: {e}")


    def show_section(self, section):
        """Переключение между разделами"""
        print(f"Активирован раздел: {section}")  # Для отладки

        # Обновляем данные при переключении на некоторые разделы
        if hasattr(self, 'current_panel'):
            if section == 'users' and hasattr(self.current_panel, 'load_users'):
                self.current_panel.load_users()
            elif section == 'students' and hasattr(self.current_panel, 'load_students'):
                self.current_panel.load_students()
            elif section == 'grades' and hasattr(self.current_panel, 'load_student_grades'):
                self.current_panel.load_student_grades()

    def logout(self):
        reply = QMessageBox.question(self, 'Подтверждение',
                                     'Вы уверены, что хотите выйти из системы?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            user_manager.logout()
            self.logout_requested.emit()
