from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QMessageBox,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
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

        # Навигационные кнопки
        nav_buttons = self.create_navigation_buttons()
        layout.addWidget(nav_buttons)

        # Кнопка выхода
        logout_btn = QPushButton("Выйти из системы")
        logout_btn.setObjectName("logout_button")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        sidebar.setLayout(layout)
        return sidebar

    def create_navigation_buttons(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Кнопки навигации в зависимости от роли
        role = user_manager.current_user['role']
        print(f"Создание навигации для роли: {role}")  # Для отладки

        if role == 'admin':
            buttons = [
                ("📊 Панель управления", "dashboard"),
                ("👥 Пользователи", "users"),
                ("🏢 Кафедры", "departments"),
                ("📋 Логи системы", "logs"),
                ("💾 Резервные копии", "backup")
            ]
        elif role == 'dekanat':
            buttons = [
                ("👥 Студенты", "students"),
                ("👨‍🏫 Преподаватели", "teachers"),
                ("📋 Учебные планы", "study_plans"),
                ("📅 Расписание", "schedule"),
                ("📊 Отчеты", "reports")
            ]
        elif role == 'teacher':
            buttons = [
                ("📚 Мои дисциплины", "disciplines"),
                ("📅 Моё расписание", "schedule"),
                ("🎯 Успеваемость", "grades"),
                ("📈 Нагрузка", "workload"),
                ("📊 Отчеты", "reports")
            ]
        elif role == 'student':
            buttons = [
                ("📖 Успеваемость", "grades"),
                ("📅 Расписание", "schedule"),
                ("📚 Зачётная книжка", "record_book"),
                ("📊 Отчеты", "reports")
            ]
        else:
            buttons = []

        for text, action in buttons:
            btn = QPushButton(text)
            btn.setObjectName("nav_button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, a=action: self.show_section(a))
            layout.addWidget(btn)

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

    def get_role_name(self, role):
        role_names = {
            'admin': 'Администратор',
            'dekanat': 'Сотрудник кафедры',
            'teacher': 'Преподаватель',
            'student': 'Студент'
        }
        return role_names.get(role, role)

    def load_initial_data(self):
        """Загрузка начальных данных в зависимости от роли"""
        role = user_manager.current_user['role']
        print(f"=== НАЧАЛО ЗАГРУЗКИ ДАННЫХ ===")
        print(f"🎯 Роль из user_manager: '{role}'")
        print(f"🔍 Полный user_manager.current_user: {user_manager.current_user}")

        try:
            if role == 'admin':
                print("👑 Создаем AdminPanel...")
                self.admin_panel = AdminPanel()
                self.stacked_widget.addWidget(self.admin_panel)
                self.current_panel = self.admin_panel
                print("✅ AdminPanel создана и добавлена")

            elif role == 'dekanat' or role == 'kafedra':
                print("🏢 Создаем DekanatPanel...")
                self.dekanat_panel = DekanatPanel()
                self.stacked_widget.addWidget(self.dekanat_panel)
                self.current_panel = self.dekanat_panel
                print("✅ DekanatPanel создана и добавлена")

            elif role == 'teacher':
                # ПРОВЕРКА ВСЕХ ВОЗМОЖНЫХ КЛЮЧЕЙ
                teacher_id = user_manager.current_user.get('teacher_db_id')
                teacher_id_alt = user_manager.current_user.get('teacher_id')
                print(f"👨‍🏫 Ключи преподавателя:")
                print(f"   teacher_db_id: {teacher_id}")
                print(f"   teacher_id: {teacher_id_alt}")
                print(f"   Все ключи: {list(user_manager.current_user.keys())}")
                # Используем любой доступный ID
                final_teacher_id = teacher_id or teacher_id_alt
                print(f"🎯 Используем teacher_id: {final_teacher_id}")
                if final_teacher_id:
                    try:
                        print("🔄 Создаем TeacherPanel...")
                        self.teacher_panel = TeacherPanel(final_teacher_id)
                        print("✅ TeacherPanel создана")
                        self.stacked_widget.addWidget(self.teacher_panel)
                        print("✅ TeacherPanel добавлена в stacked_widget")
                        self.current_panel = self.teacher_panel
                        print("✅ current_panel установлена")
                        # ПРОВЕРКА СРАЗУ ПОСЛЕ СОЗДАНИЯ
                        print(f"🔍 Проверка панели: {hasattr(self, 'teacher_panel')}")
                        print(f"📦 Stacked widget count: {self.stacked_widget.count()}")
                        print(f"🎯 Текущий виджет: {self.stacked_widget.currentWidget()}")
                    except Exception as e:
                        print(f"💥 Ошибка при создании TeacherPanel: {e}")
                        import traceback
                        traceback.print_exc()
                        QMessageBox.critical(self, "Ошибка", f"Не удалось создать панель преподавателя: {str(e)}")
                else:
                    print("❌ ID преподавателя не найден")
                    QMessageBox.warning(self, "Ошибка", "ID преподавателя не найден")

            elif role == 'student':
                # Аналогично для студента
                student_id = user_manager.current_user.get('student_db_id')
                student_id_alt = user_manager.current_user.get('student_id')

                print(f"🎓 Ключи студента:")
                print(f"   student_db_id: {student_id}")
                print(f"   student_id: {student_id_alt}")

                final_student_id = student_id or student_id_alt
                print(f"🎯 Используем student_id: {final_student_id}")

                if final_student_id:
                    self.student_panel = StudentPanel(final_student_id)
                    self.stacked_widget.addWidget(self.student_panel)
                    self.current_panel = self.student_panel
                    print("✅ StudentPanel создана и добавена")
                else:
                    print("❌ ID студента не найден")

            print(f"🎉 Панель создана для роли: '{role}'")
            print(f"📦 Тип текущей панели: {type(self.current_panel)}")
            print(f"🔢 Количество виджетов в stacked_widget: {self.stacked_widget.count()}")

        except Exception as e:
            print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить интерфейс: {str(e)}")
        print(f"🎉 Панель создана для роли: '{role}'")
        print(f"📦 Тип текущей панели: {type(self.current_panel)}")
        print(f"🔢 Количество виджетов в stacked_widget: {self.stacked_widget.count()}")

        # ДОБАВЬТЕ ЭТИ СТРОКИ:
        if self.current_panel:
            print("🔄 Устанавливаем текущую панель в stacked_widget...")
            self.stacked_widget.setCurrentWidget(self.current_panel)
            print("✅ Текущая панель установлена")
        else:
            print("❌ current_panel is None!")

        print(f"🎯 Текущий виджет в stacked_widget: {self.stacked_widget.currentWidget()}")


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