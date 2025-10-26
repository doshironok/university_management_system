import os
import platform
import subprocess
from PyQt6.QtWidgets import QMessageBox

def open_file(file_path):
    """Открытие файла в стандартной программе ОС"""
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        return True
    except Exception as e:
        return False

def show_error_message(parent, title, message):
    """Показать сообщение об ошибке"""
    QMessageBox.critical(parent, title, message)

def show_success_message(parent, title, message):
    """Показать сообщение об успехе"""
    QMessageBox.information(parent, title, message)

def validate_email(email):
    """Проверка валидности email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Проверка валидности телефона"""
    import re
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def format_date(date_string):
    """Форматирование даты в русский формат"""
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except:
        return date_string

def get_file_size(file_path):
    """Получение размера файла в читаемом формате"""
    size_bytes = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"