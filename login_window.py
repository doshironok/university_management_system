from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from user_manager import user_manager
from database import db


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Вход в систему - Учебная деятельность кафедры')

        # Использовать размеры родительского окна если есть
        if self.parent():
            parent_size = self.parent().size()
            self.resize(parent_size.width() // 2, parent_size.height() // 2)
        else:
            self.resize(400, 500)  # Размер по умолчанию

        self.center()

    def center(self):
        # Центрирование относительно родителя или экрана
        if self.parent():
            parent_geometry = self.parent().geometry()
            self.move(
                parent_geometry.center() - self.rect().center()
            )
        else:
            screen = QApplication.primaryScreen().geometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#main_frame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel#title {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel#subtitle {
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 30px;
            }
            QLineEdit {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background-color: #fafafa;
                margin-bottom: 15px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
            QPushButton#login_button {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton#login_button:hover {
                background-color: #2980b9;
            }
            QPushButton#login_button:pressed {
                background-color: #21618c;
            }
            QLabel#footer {
                color: #95a5a6;
                font-size: 12px;
                margin-top: 20px;
            }
        """)

        # Главный layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Основной фрейм
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        title_label = QLabel("Учебная деятельность кафедры")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Система управления учебным процессом")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Поля ввода
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопка входа
        login_button = QPushButton("Войти в систему")
        login_button.setObjectName("login_button")
        login_button.clicked.connect(self.handle_login)

        # Обработка нажатия Enter
        self.password_input.returnPressed.connect(self.handle_login)

        # Футер
        footer_label = QLabel("КубГТУ © 2025")
        footer_label.setObjectName("footer")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавление виджетов в layout фрейма
        frame_layout.addWidget(title_label)
        frame_layout.addWidget(subtitle_label)
        frame_layout.addWidget(QLabel("Логин:"))
        frame_layout.addWidget(self.login_input)
        frame_layout.addWidget(QLabel("Пароль:"))
        frame_layout.addWidget(self.password_input)
        frame_layout.addWidget(login_button)
        frame_layout.addWidget(footer_label)

        main_frame.setLayout(frame_layout)
        layout.addWidget(main_frame)
        self.setLayout(layout)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return

        # Подключаемся к базе данных
        if not db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        # Аутентификация
        success, message = user_manager.authenticate(login, password)

        if success:
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {user_manager.current_user['fio']}!")
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Ошибка", message)
            self.password_input.clear()