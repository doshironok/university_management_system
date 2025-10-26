import sys
import os

sys.path.append(os.path.dirname(__file__))

from widgets.role_panels import AdminPanel, DekanatPanel, TeacherPanel, StudentPanel


def check_panel_structures():
    print("=== ПРОВЕРКА СТРУКТУРЫ ПАНЕЛЕЙ ===")

    # Проверяем что панели вообще импортируются
    print("✅ AdminPanel импортирована")
    print("✅ DekanatPanel импортирована")
    print("✅ TeacherPanel импортирована")
    print("✅ StudentPanel импортирована")

    # Проверяем базовые методы
    print("\n🔍 Проверка методов AdminPanel:")
    admin_methods = [method for method in dir(AdminPanel) if not method.startswith('_')]
    print(f"Методы: {admin_methods}")

    print("\n🔍 Проверка методов DekanatPanel:")
    dekanat_methods = [method for method in dir(DekanatPanel) if not method.startswith('_')]
    print(f"Методы: {dekanat_methods}")


if __name__ == '__main__':
    check_panel_structures()