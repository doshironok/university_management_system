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

def apply_dialog_style(dialog):
    dialog.setStyleSheet("""
        QDialog {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QFrame#dialog_frame {
            background-color: white;
            border-radius: 15px;
            border: 1px solid #e0e0e0;
        }
        QLineEdit, QComboBox, QDateEdit {
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            background-color: #fafafa;
        }
        QLineEdit:focus, QComboBox:focus {
            border-color: #3498db;
            background-color: white;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #2980b9; }
        QPushButton:pressed { background-color: #21618c; }
        QLabel { color: #2c3e50; font-size: 14px; }
    """)