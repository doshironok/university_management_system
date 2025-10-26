import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Настройки приложения"""

    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'university_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

    # Настройки приложения
    APP_NAME = "Учебная деятельность кафедры"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "КубГТУ"

    # Настройки путей
    TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
    LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

    # Настройки интерфейса
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    SIDEBAR_WIDTH = 280

    # Цветовая схема
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2c3e50"
    SUCCESS_COLOR = "#27ae60"
    WARNING_COLOR = "#f39c12"
    ERROR_COLOR = "#e74c3c"

    @classmethod
    def create_directories(cls):
        """Создание необходимых директорий"""
        directories = [cls.TEMPLATES_DIR, cls.REPORTS_DIR, cls.LOGS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @classmethod
    def get_database_url(cls):
        """Получение URL для подключения к БД"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"