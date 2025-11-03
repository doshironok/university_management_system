import os
import subprocess
import logging
from datetime import datetime
from config.settings import Settings


class BackupService:
    """Сервис для создания резервных копий БД"""

    @staticmethod
    def create_backup():
        """Полноценное создание резервной копии базы данных"""
        try:
            print("🔍 ПОЛНОЦЕННОЕ СОЗДАНИЕ БЭКАПА")

            # Создаем директорию для бэкапов
            backup_dir = os.path.join(Settings.REPORTS_DIR, 'backups')
            print(f"📁 Директория бэкапов: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
            print(f"💾 Файл бэкапа: {backup_file}")

            # Пытаемся использовать pg_dump разными способами
            pg_dump_path = BackupService._find_pg_dump()

            if pg_dump_path:
                print(f"✅ Используем pg_dump: {pg_dump_path}")
                return BackupService._create_backup_with_pg_dump(pg_dump_path, backup_file)
            else:
                print("🔄 pg_dump не найден, используем Python метод")
                return BackupService._create_backup_with_python(backup_file)

        except Exception as e:
            print(f"💥 Ошибка при создании резервной копии: {e}")
            logging.error(f"Ошибка при создании резервной копии: {e}")
            return None

    @staticmethod
    def _find_pg_dump():
        """Поиск pg_dump в системе"""
        print("🔍 Поиск pg_dump в системе...")

        # Проверяем в PATH
        try:
            result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"✅ pg_dump найден в PATH: {result.stdout.strip()}")
                return 'pg_dump'
        except:
            pass

        # Ищем в стандартных путях установки PostgreSQL
        pg_paths = [
            r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\12\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\11\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\10\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\9\bin\pg_dump.exe",
        ]

        for path in pg_paths:
            if os.path.exists(path):
                print(f"✅ pg_dump найден: {path}")
                return path

        print("❌ pg_dump не найден в системе")
        return None

    @staticmethod
    def _create_backup_with_pg_dump(pg_dump_path, backup_file):
        """Создание бэкапа с помощью pg_dump"""
        try:
            print("🚀 Создание бэкапа через pg_dump...")

            # Команда для pg_dump
            cmd = [
                pg_dump_path,
                '-h', Settings.DB_HOST,
                '-p', Settings.DB_PORT,
                '-U', Settings.DB_USER,
                '-d', Settings.DB_NAME,
                '-f', backup_file,
                '-F', 'c',  # custom format
                '-v'  # verbose
            ]

            print(f"🔧 Команда: {' '.join(cmd)}")

            # Устанавливаем переменную окружения с паролем
            env = os.environ.copy()
            env['PGPASSWORD'] = Settings.DB_PASSWORD

            # Выполняем команду
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, shell=(pg_dump_path == 'pg_dump'))

            print(f"📊 Результат выполнения pg_dump:")
            print(f"   Return code: {result.returncode}")
            if result.stdout:
                print(f"   Stdout: {result.stdout}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")

            if result.returncode == 0:
                if os.path.exists(backup_file):
                    file_size = os.path.getsize(backup_file)
                    print(f"✅ Бэкап создан успешно через pg_dump: {backup_file} ({file_size} bytes)")
                    logging.info(f"Резервная копия создана через pg_dump: {backup_file}")
                    return backup_file
                else:
                    print("❌ Файл бэкапа не создан")
                    return None
            else:
                print(f"❌ Ошибка выполнения pg_dump, пробуем Python метод...")
                return BackupService._create_backup_with_python(backup_file)

        except Exception as e:
            print(f"💥 Ошибка при создании бэкапа через pg_dump: {e}")
            return BackupService._create_backup_with_python(backup_file)

    @staticmethod
    def _create_backup_with_python(backup_file):
        """Создание бэкапа через Python (полная версия)"""
        try:
            print("🔍 СОЗДАНИЕ ПОЛНОГО БЭКАПА ЧЕРЕЗ PYTHON")
            from database import db

            print(f"💾 Создаем файл: {backup_file}")

            # Получаем таблицы из базы данных
            tables_query = """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY 
              CASE tablename
                WHEN 'departments' THEN 1
                WHEN 'study_programs' THEN 2
                WHEN 'groups' THEN 3
                WHEN 'teachers' THEN 4
                WHEN 'students' THEN 5
                WHEN 'disciplines' THEN 6
                WHEN 'study_plans' THEN 7   -- ← ДО grades!
                WHEN 'classrooms' THEN 8
                WHEN 'schedule' THEN 9
                WHEN 'grades' THEN 10       -- ← После study_plans
                WHEN 'users' THEN 11
                ELSE 99
              END
            """

            tables_result = db.execute_query(tables_query)
            if not tables_result:
                print("❌ Не найдены таблицы для бэкапа")
                return None

            tables = [table[0] for table in tables_result]
            print(f"📋 Найдено таблиц: {len(tables)}")
            print(f"📋 Список таблиц: {tables}")

            with open(backup_file, 'w', encoding='utf-8') as f:
                # Заголовок файла
                f.write("-- ============================================\n")
                f.write("-- ПОЛНАЯ РЕЗЕРВНАЯ КОПИЯ БАЗЫ ДАННЫХ\n")
                f.write("-- ============================================\n")
                f.write(f"-- Создана: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- База данных: {Settings.DB_NAME}\n")
                f.write(f"-- Хост: {Settings.DB_HOST}:{Settings.DB_PORT}\n")
                f.write("-- ============================================\n\n")

                # Отключаем проверки для ускорения
                f.write("-- Отключаем проверки для ускорения импорта\n")
                f.write("SET session_replication_role = 'replica';\n")
                f.write("SET CONSTRAINTS ALL DEFERRED;\n\n")

                total_rows = 0

                # Внутри цикла по таблицам:
                for table_name in tables:
                    print(f"🔍 Обрабатываем таблицу: {table_name}")
                    try:
                        # === 1. Получаем структуру колонок ===
                        structure_query = f"""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = %s AND table_schema = 'public'
                        ORDER BY ordinal_position
                        """
                        structure = db.execute_query(structure_query, (table_name,))

                        if not structure:
                            print(f"⚠️ Не удалось получить структуру таблицы {table_name}")
                            continue

                        # === 2. Получаем PRIMARY KEY ===
                        pk_query = """
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                          ON tc.constraint_name = kcu.constraint_name
                         AND tc.table_schema = kcu.table_schema
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                          AND tc.table_name = %s
                          AND tc.table_schema = 'public'
                        ORDER BY kcu.ordinal_position
                        """
                        pk_result = db.execute_query(pk_query, (table_name,))
                        primary_keys = [row[0] for row in pk_result] if pk_result else []

                        # === 3. Получаем данные таблицы ===
                        data_query = f'SELECT * FROM "{table_name}"'
                        table_data = db.execute_query(data_query)
                        if table_data is None:
                            f.write(f"\n-- Ошибка чтения таблицы: {table_name}\n")
                            continue

                        # === 4. Записываем DROP и CREATE TABLE ===
                        f.write(f"\n-- ============================================\n")
                        f.write(f"-- ТАБЛИЦА: {table_name}\n")
                        f.write(f"-- ============================================\n")
                        f.write(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;\n')
                        f.write(f'CREATE TABLE "{table_name}" (\n')

                        columns_def = []
                        for col in structure:
                            col_name, data_type, is_nullable, col_default = col
                            # Приведение типов
                            if 'character' in data_type:
                                data_type = 'TEXT'
                            elif 'timestamp' in data_type:
                                data_type = 'TIMESTAMP'
                            elif 'boolean' in data_type:
                                data_type = 'BOOLEAN'
                            elif 'integer' in data_type:
                                data_type = 'INTEGER'

                            col_def = f'    "{col_name}" {data_type}'
                            if is_nullable == 'NO':
                                col_def += " NOT NULL"
                            if col_default:
                                col_def += f" DEFAULT {col_default}"
                            columns_def.append(col_def)

                        f.write(',\n'.join(columns_def))

                        # Добавляем PRIMARY KEY, если есть
                        if primary_keys:
                            pk_cols = ', '.join([f'"{col}"' for col in primary_keys])
                            f.write(f',\n    CONSTRAINT "{table_name}_pkey" PRIMARY KEY ({pk_cols})')

                        f.write("\n);\n")

                        # === 5. Вставляем данные ===
                        if table_data:
                            col_names = [col[0] for col in structure]
                            f.write(f"-- Данные таблицы {table_name} ({len(table_data)} записей)\n")
                            f.write(
                                f'INSERT INTO "{table_name}" ({", ".join([f"\"{c}\"" for c in col_names])}) VALUES\n')
                            rows = []
                            for row in table_data:
                                formatted_values = []
                                for value in row:
                                    if value is None:
                                        formatted_values.append("NULL")
                                    elif isinstance(value, str):
                                        escaped_value = value.replace("'", "''").replace("\n", "\\n").replace("\r",
                                                                                                              "\\r")
                                        formatted_values.append(f"'{escaped_value}'")
                                    elif isinstance(value, datetime):
                                        # Для даты без времени — только дата в формате 'YYYY-MM-DD'
                                        if value.time().hour == 0 and value.time().minute == 0 and value.time().second == 0:
                                            formatted_values.append(f"'{value.strftime('%Y-%m-%d')}'")
                                        else:
                                            formatted_values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                                    elif isinstance(value, bool):
                                        formatted_values.append("TRUE" if value else "FALSE")
                                    else:
                                        formatted_values.append(str(value))
                                rows.append(f"({', '.join(formatted_values)})")
                            f.write(',\n'.join(rows))
                            f.write(";\n")

                            # === 6. Сбрасываем последовательность (если есть SERIAL-поле) ===
                            # Ищем колонку с именем *_id и DEFAULT nextval(...)
                            for col in structure:
                                col_name, _, _, col_default = col
                                if col_name == 'id' or col_name.endswith('_id'):
                                    if col_default and 'nextval' in col_default:
                                        # Извлекаем имя последовательности из col_default, например: nextval('teachers_id_seq'::regclass)
                                        import re
                                        seq_match = re.search(r"nextval\('([^']+)'", col_default)
                                        if seq_match:
                                            seq_name = seq_match.group(1)
                                            f.write(
                                                f"SELECT setval('{seq_name}', (SELECT MAX({col_name}) FROM \"{table_name}\"));\n")
                                            break
                        else:
                            f.write(f"-- Таблица {table_name} пуста\n")

                    except Exception as e:
                        print(f"⚠️ Ошибка при обработке таблицы {table_name}: {e}")
                        f.write(f"\n-- Ошибка при обработке таблицы {table_name}: {e}\n")
                        continue

                # Включаем проверки обратно
                f.write("\n-- Включаем проверки обратно\n")
                f.write("SET session_replication_role = 'origin';\n")
                f.write("-- ============================================\n")
                f.write(f"-- ВСЕГО: {len(tables)} таблиц, {total_rows} записей\n")
                f.write("-- ============================================\n")

            file_size = os.path.getsize(backup_file)
            print(f"✅ Полный Python бэкап создан: {backup_file} ({file_size} bytes, {total_rows} записей)")
            return backup_file

        except Exception as e:
            print(f"💥 Ошибка создания полного Python бэкапа: {e}")
            import traceback
            traceback.print_exc()
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
        """Восстановление из резервной копии с детальной диагностикой"""
        try:
            print("🔄 ЗАПУСК ВОССТАНОВЛЕНИЯ ИЗ БЭКАПА")
            print(f"📁 Файл бэкапа: {backup_file}")

            # Проверяем существование файла
            if not os.path.exists(backup_file):
                print(f"❌ Файл бэкапа не существует: {backup_file}")
                return False

            file_size = os.path.getsize(backup_file)
            print(f"📊 Размер файла: {file_size} байт")

            # Определяем тип бэкапа
            backup_type = BackupService._detect_backup_type(backup_file)
            print(f"🔍 Тип бэкапа: {backup_type}")

            if backup_type == 'pg_dump_custom':
                print("🎯 Восстанавливаем через pg_restore...")
                return BackupService._restore_with_pg_restore(backup_file)
            elif backup_type == 'sql_script':
                print("🎯 Восстанавливаем через SQL скрипт...")
                return BackupService._restore_with_sql_script(backup_file)
            else:
                print("❌ Неизвестный формат бэкапа")
                return False

        except Exception as e:
            print(f"💥 Ошибка при восстановлении бэкапа: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _detect_backup_type(backup_file):
        """Определение типа бэкапа"""
        try:
            # Проверяем первые байты файла для определения формата
            with open(backup_file, 'rb') as f:
                first_bytes = f.read(100)

            # pg_dump custom format имеет специальную сигнатуру
            if first_bytes.startswith(b'PGDMP'):
                return 'pg_dump_custom'
            # SQL скрипт обычно начинается с комментариев или SQL команд
            elif b'--' in first_bytes or b'CREATE' in first_bytes or b'INSERT' in first_bytes:
                return 'sql_script'
            else:
                return 'unknown'
        except:
            return 'unknown'

    @staticmethod
    def _restore_with_pg_restore(backup_file):
        """Восстановление через pg_restore"""
        try:
            print("🔍 Поиск pg_restore...")
            pg_restore_path = BackupService._find_pg_restore()

            if not pg_restore_path:
                print("❌ pg_restore не найден, пробуем SQL метод...")
                return BackupService._restore_with_sql_script(backup_file)

            # Команда для pg_restore
            cmd = [
                pg_restore_path,
                '-h', Settings.DB_HOST,
                '-p', Settings.DB_PORT,
                '-U', Settings.DB_USER,
                '-d', Settings.DB_NAME,
                '-c',  # clean (drop objects before recreating)
                '-v',  # verbose
                backup_file
            ]

            print(f"🔧 Команда восстановления: {' '.join(cmd)}")

            # Устанавливаем переменную окружения с паролем
            env = os.environ.copy()
            env['PGPASSWORD'] = Settings.DB_PASSWORD

            # Выполняем команду
            print("🚀 Выполняем восстановление через pg_restore...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True,
                                    shell=(pg_restore_path == 'pg_restore'))

            print(f"📊 Результат выполнения pg_restore:")
            print(f"   Return code: {result.returncode}")
            if result.stdout:
                print(f"   Stdout: {result.stdout}")
            if result.stderr:
                print(f"   Stderr: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"💥 Ошибка при восстановлении через pg_restore: {e}")
            return False

    @staticmethod
    def _find_pg_restore():
        """Поиск pg_restore в системе"""
        # Проверяем в PATH
        try:
            result = subprocess.run(['pg_restore', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"✅ pg_restore найден в PATH: {result.stdout.strip()}")
                return 'pg_restore'
        except:
            pass

        # Ищем в стандартных путях
        pg_paths = [
            r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_restore.exe",
            r"C:\Program Files\PostgreSQL\14\bin\pg_restore.exe",
            r"C:\Program Files\PostgreSQL\13\bin\pg_restore.exe",
            r"C:\Program Files\PostgreSQL\12\bin\pg_restore.exe",
            r"C:\Program Files\PostgreSQL\11\bin\pg_restore.exe",
        ]

        for path in pg_paths:
            if os.path.exists(path):
                print(f"✅ pg_restore найден: {path}")
                return path

        return None

    @staticmethod
    def _restore_with_sql_script(backup_file):
        """Восстановление через выполнение SQL скрипта В ОДНОЙ ТРАНЗАКЦИИ"""
        try:
            print("🔍 Восстановление через SQL скрипт в одной транзакции...")
            from database import db

            if not db.connect():
                print("❌ Не удалось подключиться к БД")
                return False

            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            print(f"📖 Размер SQL скрипта: {len(sql_script)} символов")

            # === Выполняем ВЕСЬ скрипт в одной транзакции ===
            old_autocommit = db.connection.autocommit
            db.connection.autocommit = False  # Отключаем автокоммит

            try:
                db.cursor.execute(sql_script)  # Вся логика — в одном execute
                db.connection.commit()
                print("✅ SQL-бэкап восстановлен успешно в одной транзакции")
                return True
            except Exception as e:
                db.connection.rollback()
                print(f"❌ Ошибка при восстановлении: {e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                db.connection.autocommit = old_autocommit  # Восстанавливаем

        except Exception as e:
            print(f"💥 Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _split_sql_commands(sql_script):
        """Разбивает SQL скрипт на отдельные команды"""
        commands = []
        current_command = ""

        lines = sql_script.split('\n')
        in_string = False
        string_char = None

        for line in lines:
            line = line.strip()

            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('--'):
                continue

            # Обрабатываем строки с учетом строковых литералов
            i = 0
            while i < len(line):
                char = line[i]

                if char in ("'", '"') and not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and in_string:
                    # Проверяем не экранирована ли кавычка
                    if i > 0 and line[i - 1] == '\\':
                        pass  # Экранированная кавычка, игнорируем
                    else:
                        in_string = False
                        string_char = None
                elif char == ';' and not in_string:
                    # Конец команды
                    current_command += line[:i + 1]
                    if current_command.strip():
                        commands.append(current_command.strip())
                    current_command = ""
                    line = line[i + 1:]
                    i = -1  # Сброс индекса для оставшейся части строки

                i += 1

            # Добавляем оставшуюся часть строки к текущей команде
            if line:
                current_command += line + " "

        # Добавляем последнюю команду если она есть
        if current_command.strip():
            commands.append(current_command.strip())

        return commands

