import bcrypt
from database import db


class UserManager:
    def __init__(self):
        self.current_user = None

    def verify_password(self, plain_password, hashed_password):
        """Проверка пароля"""
        try:
            if not hashed_password:
                return False
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            print(f"Ошибка проверки пароля: {e}")
            return False

    def hash_password(self, password):
        """Хеширование пароля"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, login, password):
        """Аутентификация пользователя"""
        print(f"🔐 Попытка аутентификации для: {login}")

        user_data = db.get_user_by_login(login)
        if not user_data:
            print(f"❌ Пользователь {login} не найден")
            return False, "Пользователь не найден"

        print(f"📊 Данные из БД: {user_data}")

        # Проверяем пароль
        if not self.verify_password(password, user_data[2]):  # password_hash
            print(f"❌ Неверный пароль для {login}")
            return False, "Неверный пароль"

        # Определяем роль
        role = user_data[3]  # role из БД
        print(f"🎯 Определена роль: {role}")

        # Создаем объект пользователя
        self.current_user = {
            'id': user_data[0],
            'login': user_data[1],
            'role': role,
            'teacher_id': user_data[4],
            'student_id': user_data[5],
            'department_id': user_data[6],
            'teacher_fio': user_data[7] if len(user_data) > 7 else None,
            'student_fio': user_data[8] if len(user_data) > 8 else None,
            'teacher_db_id': user_data[9] if len(user_data) > 9 else None,
            'student_db_id': user_data[10] if len(user_data) > 10 else None,
            'fio': (user_data[7] or user_data[8] or 'Администратор') if len(user_data) > 8 else 'Пользователь'
        }

        print(f"✅ Успешная аутентификация: {self.current_user}")

        return True, "Успешная аутентификация"

    def logout(self):
        """Выход пользователя"""
        self.current_user = None

    def get_current_user(self):
        """Получение текущего пользователя"""
        return self.current_user

    def has_role(self, role):
        """Проверка роли пользователя"""
        return self.current_user and self.current_user['role'] == role


# Глобальный экземпляр менеджера пользователей
user_manager = UserManager()