import os
import subprocess
import logging
from datetime import datetime
from config.settings import Settings


class BackupService:
    """Сервис для создания резервных копий БД"""

    @staticmethod
    def create_backup():
        """Создание резервной копии базы данных"""
        try:
            # Создаем директорию для бэкапов если её нет
            backup_dir = os.path.join(Settings.REPORTS_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            # Формируем имя файла с датой
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')

            # Команда для pg_dump
            cmd = [
                'pg_dump',
                '-h', Settings.DB_HOST,
                '-p', Settings.DB_PORT,
                '-U', Settings.DB_USER,
                '-d', Settings.DB_NAME,
                '-f', backup_file,
                '-F', 'c'  # custom format
            ]

            # Устанавливаем переменную окружения с паролем
            env = os.environ.copy()
            env['PGPASSWORD'] = Settings.DB_PASSWORD

            # Выполняем команду
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                logging.info(f"Резервная копия создана: {backup_file}")
                return backup_file
            else:
                logging.error(f"Ошибка создания резервной копии: {result.stderr}")
                return None

        except Exception as e:
            logging.error(f"Ошибка при создании резервной копии: {e}")
            return None

    @staticmethod
    def get_backup_list():
        """Получение списка резервных копий"""
        backup_dir = os.path.join(Settings.REPORTS_DIR, 'backups')
        if not os.path.exists(backup_dir):
            return []

        backups = []
        for file in os.listdir(backup_dir):
            if file.endswith('.sql'):
                file_path = os.path.join(backup_dir, file)
                file_time = os.path.getmtime(file_path)
                file_size = os.path.getsize(file_path)

                backups.append({
                    'filename': file,
                    'path': file_path,
                    'size': file_size,
                    'created': datetime.fromtimestamp(file_time).strftime('%d.%m.%Y %H:%M:%S')
                })

        # Сортируем по дате создания (новые сначала)
        backups.sort(key=lambda x: x['path'], reverse=True)
        return backups

    @staticmethod
    def restore_backup(backup_file):
        """Восстановление из резервной копии"""
        try:
            # Команда для pg_restore
            cmd = [
                'pg_restore',
                '-h', Settings.DB_HOST,
                '-p', Settings.DB_PORT,
                '-U', Settings.DB_USER,
                '-d', Settings.DB_NAME,
                '-c',  # clean (drop) database objects before recreating
                backup_file
            ]

            # Устанавливаем переменную окружения с паролем
            env = os.environ.copy()
            env['PGPASSWORD'] = Settings.DB_PASSWORD

            # Выполняем команду
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                logging.info(f"База данных восстановлена из: {backup_file}")
                return True
            else:
                logging.error(f"Ошибка восстановления БД: {result.stderr}")
                return False

        except Exception as e:
            logging.error(f"Ошибка при восстановлении БД: {e}")
            return False