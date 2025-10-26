import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from login_window import LoginWindow
from main_window import MainWindow
from database import db
from config.settings import Settings


# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


class UniversityApp:
    def __init__(self):
        # Создаем необходимые директории
        Settings.create_directories()

        # Настраиваем логирование
        setup_logging()

        self.logger = logging.getLogger(__name__)
        self.app = QApplication(sys.argv)

        # Настройка шрифтов приложения
        self.setup_fonts()

        # Настройка стилей
        self.setup_styles()

        self.login_window = LoginWindow()
        self.main_window = None

        # Подключаем сигналы
        self.login_window.login_successful.connect(self.show_main_window)

        self.logger.info("Приложение инициализировано")

    def setup_fonts(self):
        """Настройка шрифтов приложения"""
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

    def setup_styles(self):
        """Настройка стилей приложения"""
        self.app.setStyle('Fusion')

    def show_main_window(self):
        """Показать главное окно после успешного входа"""
        try:
            self.main_window = MainWindow()
            self.main_window.logout_requested.connect(self.logout)
            self.main_window.show()
            self.login_window.hide()
            self.logger.info("Главное окно открыто")
        except Exception as e:
            self.logger.error(f"Ошибка при открытии главного окна: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть главное окно: {str(e)}")

    def logout(self):
        """Выход из системы"""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            self.logger.info("Главное окно закрыто")

        db.disconnect()
        self.login_window.show()
        self.login_window.password_input.clear()
        self.logger.info("Пользователь вышел из системы")

    def run(self):
        """Запуск приложения"""
        self.logger.info("Запуск приложения")
        self.login_window.show()

        # Таймер для периодической проверки соединения с БД
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_database_connection)
        self.connection_timer.start(30000)  # Проверка каждые 30 секунд

        return_code = self.app.exec()

        # Очистка при завершении
        self.connection_timer.stop()
        db.disconnect()
        self.logger.info("Приложение завершено")

        return return_code

    def check_database_connection(self):
        """Периодическая проверка соединения с БД"""
        try:
            if db.connection and not db.connection.closed:
                db.cursor.execute("SELECT 1")
        except Exception as e:
            self.logger.warning(f"Потеряно соединение с БД: {e}")
            # Попытка переподключения
            if self.main_window:
                db.connect()


if __name__ == '__main__':
    try:
        university_app = UniversityApp()
        sys.exit(university_app.run())
    except Exception as e:
        logging.critical(f"Критическая ошибка при запуске приложения: {e}")
        from PyQt6.QtWidgets import QMessageBox

        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Критическая ошибка",
                             f"Не удалось запустить приложение:\n{str(e)}")
        sys.exit(1)