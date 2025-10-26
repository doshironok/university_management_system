import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import db
from user_manager import user_manager


def debug_authentication():
    print("=== ДЕБАГ АУТЕНТИФИКАЦИИ ===")

    if not db.connect():
        print("❌ Не удалось подключиться к БД")
        return

    # Тестируем разных пользователей
    test_cases = [
        ('admin', 'admin123'),
        ('dekanat', 'dekanat123'),
        ('i.ivanov', 'teacher123'),
        ('m.alekseev', 'student123')
    ]

    for login, password in test_cases:
        print(f"\n--- Тестируем: {login} ---")

        # Сначала проверим что возвращает БД
        user_data = db.get_user_by_login(login)
        print(f"Данные из БД: {user_data}")

        if user_data:
            print(f"Роль из БД: {user_data[3]}")
            print(f"teacher_id из БД: {user_data[4]}")
            print(f"student_id из БД: {user_data[5]}")

        # Тестируем аутентификацию
        success, message = user_manager.authenticate(login, password)
        print(f"Аутентификация: {success} - {message}")

        if success:
            current_user = user_manager.get_current_user()
            print(f"Текущий пользователь: {current_user}")
            print(f"Определенная роль: {current_user['role']}")

        user_manager.logout()
        print("---")


if __name__ == '__main__':
    debug_authentication()