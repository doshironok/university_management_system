import bcrypt
from database import db


def hash_password(password: str) -> str:
    """Генерирует bcrypt-хэш для пароля."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')


def update_user_passwords():
    """Обновляет пароли всех пользователей в БД."""

    # Словарь: логин -> пароль
    users_passwords = {
        'admin': 'admin123',
        'sys.admin': 'admin123',
        'kafedra_head': 'kafedra123',
        'i.ivanov': 'teacher123',
        'a.smirnova': 'teacher123',
        'd.kuznetsov': 'teacher123',
        'm.alekseev': 'student123',
        's.belova': 'student123',
        'i.vasilev': 'student123',
        'm.grigorieva': 'student123',
        'a.dmitriev': 'student123',
    }

    print("🔐 Генерация новых хэшей паролей...")

    for login, password in users_passwords.items():
        # Генерируем новый хэш
        hashed = hash_password(password)

        # Обновляем в БД
        query = "UPDATE users SET password_hash = %s WHERE login = %s"
        result = db.execute_query(query, (hashed, login))

        if result:
            print(f"✅ Обновлен пароль для: {login}")
        else:
            print(f"❌ Ошибка при обновлении пароля для: {login}")

    print("\n✨ Готово! Теперь можно войти в приложение.")
    print("\n📋 Учетные данные:")
    for login, password in users_passwords.items():
        print(f"  • {login}: {password}")


if __name__ == "__main__":
    # Подключаемся к БД
    if db.connect():
        update_user_passwords()
        db.disconnect()
    else:
        print("❌ Не удалось подключиться к базе данных")
