import os
import psycopg2
from psycopg2 import sql
import os
import psycopg2
from psycopg2 import sql

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("Предупреждение: python-dotenv не установлен, используем переменные окружения напрямую")


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            self.cursor = self.connection.cursor()
            print("Успешное подключение к базе данных")
            return True
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Соединение с базой данных закрыто")

    def execute_query(self, query, params=None, fetch=True):
        """Выполнение SQL запроса"""
        try:
            self.cursor.execute(query, params or ())
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    return self.cursor.fetchall()
                else:
                    self.connection.commit()
                    return True
            else:
                self.connection.commit()
                return True
        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            return False

    def get_user_by_login(self, login):
        """Получение пользователя по логину"""
        query = """
        SELECT u.id, u.login, u.password_hash, u.role, 
               u.teacher_id, u.student_id,
               t.fio as teacher_fio, s.fio as student_fio,
               t.id as teacher_db_id, s.id as student_db_id
        FROM users u
        LEFT JOIN teachers t ON u.teacher_id = t.id
        LEFT JOIN students s ON u.student_id = s.id
        WHERE u.login = %s
        """
        result = self.execute_query(query, (login,))
        return result[0] if result else None


# Глобальный экземпляр базы данных
db = Database()