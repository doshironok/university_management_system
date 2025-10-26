import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import db
from user_manager import UserManager
from widgets.role_panels import AdminPanel, DekanatPanel, TeacherPanel, StudentPanel


def diagnose_role_loading():
    print("=== ДИАГНОСТИКА ЗАГРУЗКИ РОЛЕЙ ===")

    if not db.connect():
        print("❌ Не удалось подключиться к БД")
        return

    test_users = [
        ('admin', 'admin123'),
        ('dekanat', 'dekanat123'),
        ('i.ivanov', 'teacher123'),
        ('m.alekseev', 'student123')
    ]

    user_manager = UserManager()

    for login, password in test_users:
        print(f"\n{'=' * 50}")
        print(f"ТЕСТИРУЕМ: {login}")
        print(f"{'=' * 50}")

        # Аутентифицируем пользователя
        success, message = user_manager.authenticate(login, password)
        print(f"Аутентификация: {success} - {message}")

        if not success:
            continue

        current_user = user_manager.get_current_user()
        role = current_user['role']
        print(f"📋 Роль пользователя: '{role}'")
        print(f"📊 Данные пользователя: {current_user}")

        # Пробуем создать соответствующую панель
        print(f"\n🔄 Попытка создать панель для роли '{role}':")

        try:
            if role == 'admin':
                print("Создаем AdminPanel...")
                panel = AdminPanel()
                print("✅ AdminPanel создана успешно")
                print(f"Тип панели: {type(panel)}")

            elif role == 'dekanat':
                print("Создаем DekanatPanel...")
                panel = DekanatPanel()
                print("✅ DekanatPanel создана успешно")
                print(f"Тип панели: {type(panel)}")

            elif role == 'prepod':
                teacher_id = current_user.get('teacher_db_id')
                print(f"Создаем TeacherPanel с teacher_db_id: {teacher_id}")
                if teacher_id:
                    panel = TeacherPanel(teacher_id)
                    print("✅ TeacherPanel создана успешно")
                    print(f"Тип панели: {type(panel)}")
                else:
                    print("❌ teacher_db_id не найден!")

            elif role == 'student':
                student_id = current_user.get('student_db_id')
                print(f"Создаем StudentPanel с student_db_id: {student_id}")
                if student_id:
                    panel = StudentPanel(student_id)
                    print("✅ StudentPanel создана успешно")
                    print(f"Тип панели: {type(panel)}")
                else:
                    print("❌ student_db_id не найден!")

            else:
                print(f"❌ Неизвестная роль: {role}")

        except Exception as e:
            print(f"💥 ОШИБКА при создании панели: {e}")
            import traceback
            traceback.print_exc()

        user_manager.logout()
        print(f"{'=' * 50}")


if __name__ == '__main__':
    diagnose_role_loading()