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
        """Выполнение SQL запроса с правильной логикой коммита"""
        if not self.connection or self.connection.closed:
            print("Ошибка: нет соединения с базой данных")
            return False

        try:
            self.cursor.execute(query, params or ())

            # Определяем тип запроса
            query_type = query.strip().upper().split()[0]

            if query_type == 'SELECT':
                return self.cursor.fetchall() if fetch else True
            else:
                # Для INSERT/UPDATE/DELETE всегда коммитим
                self.connection.commit()
                return True

        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            return False

    def get_user_by_login(self, login):
        query = """
        SELECT u.id, u.login, u.password_hash, u.role, 
               u.teacher_id, u.student_id, u.department_id,
               t.fio as teacher_fio, s.fio as student_fio,
               t.id as teacher_db_id, s.id as student_db_id
        FROM users u
        LEFT JOIN teachers t ON u.teacher_id = t.id
        LEFT JOIN students s ON u.student_id = s.id
        WHERE u.login = %s
        """
        result = self.execute_query(query, (login,))
        return result[0] if result else None

    def execute_vacuum(self):
        """Выполнение VACUUM вне транзакции"""
        try:
            # Закрываем текущую транзакцию если есть
            if self.connection:
                self.connection.commit()

            # Выполняем VACUUM без транзакции
            self.cursor.execute("VACUUM ANALYZE")
            print("✅ VACUUM ANALYZE выполнен успешно")
            return True

        except Exception as e:
            print(f"Ошибка выполнения VACUUM: {e}")
            # Пытаемся восстановить соединение
            try:
                self.connection.rollback()
            except:
                pass
            return False

    def execute_without_transaction(self, query):
        """Выполнение запроса без транзакции"""
        try:
            # Закрываем текущую транзакцию
            if self.connection:
                self.connection.commit()

            # Устанавливаем autocommit для этого запроса
            old_autocommit = self.connection.autocommit
            self.connection.autocommit = True

            self.cursor.execute(query)

            # Восстанавливаем предыдущее состояние
            self.connection.autocommit = old_autocommit

            return True

        except Exception as e:
            print(f"Ошибка выполнения запроса без транзакции: {e}")
            # Пытаемся восстановить соединение
            try:
                self.connection.autocommit = False
                self.connection.rollback()
            except:
                pass
            return False

# Глобальный экземпляр базы данных
db = Database()