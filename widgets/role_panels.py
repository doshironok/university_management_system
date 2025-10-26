from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QComboBox, QMessageBox,
                             QTabWidget, QFormLayout, QGroupBox, QTextEdit,
                             QDateEdit, QSpinBox, QCheckBox, QDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from database import db
from widgets.report_dialogs import ReportGenerationThread


class BasePanel(QWidget):
    """Базовый класс для всех ролевых панелей"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def create_table(self, headers, data=None):
        """Создание таблицы с заданными заголовками"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
        """)

        if data:
            self.populate_table(table, data)

        return table

    def populate_table(self, table, data):
        """Заполнение таблицы данными"""
        table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                table.setItem(row_idx, col_idx, item)


class AdminPanel(BasePanel):
    """Панель администратора"""

    def __init__(self):
        super().__init__()

    def setup_ui(self):
        super().setup_ui()

        # Заголовок
        title = QLabel("Панель администратора")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(title)

        # Вкладки
        tabs = QTabWidget()

        # Вкладка пользователей
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "👥 Пользователи")

        # Вкладка кафедр
        departments_tab = self.create_departments_tab()
        tabs.addTab(departments_tab, "🏢 Кафедры")

        # Вкладка системных логов
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "📋 Логи системы")

        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "💾 Резервные копии")

        self.layout.addWidget(tabs)

    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Панель управления
        control_panel = QHBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_users)

        control_panel.addWidget(refresh_btn)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица пользователей
        self.users_table = self.create_table([
            "ID", "Логин", "Роль", "Преподаватель", "Студент"
        ])
        layout.addWidget(self.users_table)

        widget.setLayout(layout)
        return widget

    def create_departments_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Форма добавления кафедры
        form_group = QGroupBox("Добавить кафедру")
        form_layout = QFormLayout()

        self.dept_name_input = QLineEdit()
        self.dept_short_name_input = QLineEdit()

        form_layout.addRow("Название:", self.dept_name_input)
        form_layout.addRow("Сокращение:", self.dept_short_name_input)

        add_btn = QPushButton("Добавить кафедру")
        add_btn.clicked.connect(self.add_department)

        form_layout.addRow(add_btn)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Таблица кафедр
        self.departments_table = self.create_table([
            "ID", "Название", "Сокращение"  # Убрали "Дата создания"
        ])
        layout.addWidget(self.departments_table)

        widget.setLayout(layout)
        return widget

    def create_logs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.logs_table = self.create_table([
            "ID", "Пользователь", "Таблица", "Действие", "Время", "ID записи"
        ])
        layout.addWidget(self.logs_table)

        widget.setLayout(layout)
        return widget

    def load_users(self):
        """Загрузка пользователей"""
        query = """
        SELECT u.id, u.login, u.role, 
               COALESCE(t.fio, 'Нет'), 
               COALESCE(s.fio, 'Нет')
        FROM users u
        LEFT JOIN teachers t ON u.teacher_id = t.id
        LEFT JOIN students s ON u.student_id = s.id
        ORDER BY u.id
        """
        result = db.execute_query(query)
        if result:
            self.populate_table(self.users_table, result)

    def add_department(self):
        """Добавление новой кафедры"""
        name = self.dept_name_input.text().strip()
        short_name = self.dept_short_name_input.text().strip()

        if not name or not short_name:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        query = "INSERT INTO departments (name, short_name) VALUES (%s, %s)"
        if db.execute_query(query, (name, short_name), fetch=False):
            QMessageBox.information(self, "Успех", "Кафедра добавлена")
            self.dept_name_input.clear()
            self.dept_short_name_input.clear()
            self.load_departments()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить кафедру")

    def load_departments(self):
        """Загрузка кафедр"""
        query = "SELECT id, name, short_name FROM departments ORDER BY id"
        result = db.execute_query(query)
        if result:
            self.populate_table(self.departments_table, result)

    def load_logs(self):
        """Загрузка логов"""
        query = """
        SELECT id, user_name, table_name, action_type, action_time, record_id 
        FROM audit_logs 
        ORDER BY action_time DESC 
        LIMIT 100
        """
        result = db.execute_query(query)
        if result:
            self.populate_table(self.logs_table, result)

    def create_backup_tab(self):
        """Вкладка управления резервными копиями"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Информация о БД
        info_group = QGroupBox("Информация о базе данных")
        info_layout = QFormLayout()

        self.db_size_label = QLabel("Загрузка...")
        self.db_tables_label = QLabel("Загрузка...")
        self.last_backup_label = QLabel("Загрузка...")

        info_layout.addRow("Размер базы данных:", self.db_size_label)
        info_layout.addRow("Количество таблиц:", self.db_tables_label)
        info_layout.addRow("Последний бэкап:", self.last_backup_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Кнопки управления
        button_layout = QHBoxLayout()

        backup_btn = QPushButton("Создать резервную копию")
        manage_btn = QPushButton("Управление бэкапами")
        vacuum_btn = QPushButton("Оптимизировать БД")

        backup_btn.clicked.connect(self.create_backup)
        manage_btn.clicked.connect(self.manage_backups)
        vacuum_btn.clicked.connect(self.optimize_database)

        button_layout.addWidget(backup_btn)
        button_layout.addWidget(manage_btn)
        button_layout.addWidget(vacuum_btn)

        layout.addLayout(button_layout)

        # Загрузка информации при открытии вкладки
        self.load_database_info()

        widget.setLayout(layout)
        return widget

    def load_database_info(self):
        """Загрузка информации о базе данных"""
        try:
            # Размер БД
            size_query = """
               SELECT pg_size_pretty(pg_database_size(current_database()))
               """
            size_result = db.execute_query(size_query)
            if size_result:
                self.db_size_label.setText(size_result[0][0])

            # Количество таблиц
            tables_query = """
               SELECT COUNT(*) FROM information_schema.tables 
               WHERE table_schema = 'public'
               """
            tables_result = db.execute_query(tables_query)
            if tables_result:
                self.db_tables_label.setText(str(tables_result[0][0]))

            # Последний бэкап
            from services.backup_service import BackupService
            backups = BackupService.get_backup_list()
            if backups:
                self.last_backup_label.setText(backups[0]['created'])
            else:
                self.last_backup_label.setText("Нет бэкапов")

        except Exception as e:
            self.db_size_label.setText("Ошибка")
            self.db_tables_label.setText("Ошибка")
            self.last_backup_label.setText("Ошибка")

    def create_backup(self):
        """Создание резервной копии"""
        from widgets.backup_dialog import BackupThread
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt

        progress = QProgressDialog("Создание резервной копии...", "Отмена", 0, 0, self)
        progress.setWindowTitle("Пожалуйста, подождите")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        self.backup_thread = BackupThread()
        self.backup_thread.finished.connect(lambda path: self.on_backup_created(path, progress))
        self.backup_thread.error.connect(lambda error: self.on_backup_error(error, progress))
        self.backup_thread.start()

    def on_backup_created(self, file_path, progress):
        """Обработка успешного создания бэкапа"""
        progress.close()
        QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{file_path}")
        self.load_database_info()

    def on_backup_error(self, error, progress):
        """Обработка ошибки создания бэкапа"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию:\n{error}")

    def manage_backups(self):
        """Управление резервными копиями"""
        from widgets.backup_dialog import BackupDialog
        dialog = BackupDialog(self)
        dialog.exec()
        self.load_database_info()

    def optimize_database(self):
        """Оптимизация базы данных"""
        reply = QMessageBox.question(
            self,
            "Оптимизация базы данных",
            "Выполнить оптимизацию (VACUUM ANALYZE) базы данных?\n\n"
            "Эта операция может занять некоторое время.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                progress = QProgressDialog("Оптимизация базы данных...", "Отмена", 0, 0, self)
                progress.setWindowTitle("Пожалуйста, подождите")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()

                # Выполняем VACUUM ANALYZE
                db.execute_query("VACUUM ANALYZE", fetch=False)

                progress.close()
                QMessageBox.information(self, "Успех", "Оптимизация базы данных завершена")
                self.load_database_info()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось оптимизировать БД:\n{str(e)}")


class DekanatPanel(BasePanel):
    """Панель сотрудника кафедры"""

    def __init__(self):
        super().__init__()

    def setup_ui(self):
        super().setup_ui()

        title = QLabel("Панель сотрудника кафедры")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(title)

        tabs = QTabWidget()

        # Студенты
        students_tab = self.create_students_tab()
        tabs.addTab(students_tab, "👥 Студенты")

        # Преподаватели
        teachers_tab = self.create_teachers_tab()
        tabs.addTab(teachers_tab, "👨‍🏫 Преподаватели")

        # Учебные планы
        plans_tab = self.create_study_plans_tab()
        tabs.addTab(plans_tab, "📋 Учебные планы")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Расписание")

        # Добавляем вкладку отчетов
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_groups()
        self.load_students()
        self.load_teachers()
        self.load_study_plans()
        self.load_schedule()


    def create_teachers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.teachers_table = self.create_table([
            "ID", "ФИО", "Должность", "Учёная степень", "Кафедра"
        ])
        layout.addWidget(self.teachers_table)

        widget.setLayout(layout)
        return widget

    def create_study_plans_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.plans_table = self.create_table([
            "ID", "Дисциплина", "Группа", "Преподаватель", "Семестр", "Часы (лек/пр)"
        ])
        layout.addWidget(self.plans_table)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.schedule_table = self.create_table([
            "ID", "Дисциплина", "Группа", "Преподаватель", "Аудитория", "Время", "Тип недели"
        ])
        layout.addWidget(self.schedule_table)

        widget.setLayout(layout)
        return widget

    def load_groups(self):
        """Загрузка групп для фильтра"""
        query = "SELECT id, name FROM groups ORDER BY name"
        result = db.execute_query(query)
        if result:
            for group_id, group_name in result:
                self.group_filter.addItem(group_name, group_id)

    def load_students(self):
        """Загрузка студентов"""
        group_id = self.group_filter.currentData()

        if group_id:
            query = """
            SELECT s.id, s.fio, s.record_book_id, g.name, 
                   CASE WHEN s.status THEN 'Активен' ELSE 'Отчислен' END
            FROM students s
            JOIN groups g ON s.group_id = g.id
            WHERE s.group_id = %s
            ORDER BY s.fio
            """
            params = (group_id,)
        else:
            query = """
            SELECT s.id, s.fio, s.record_book_id, g.name, 
                   CASE WHEN s.status THEN 'Активен' ELSE 'Отчислен' END
            FROM students s
            JOIN groups g ON s.group_id = g.id
            ORDER BY g.name, s.fio
            """
            params = None

        result = db.execute_query(query, params)
        if result:
            self.populate_table(self.students_table, result)

    def load_teachers(self):
        """Загрузка преподавателей"""
        query = """
        SELECT t.id, t.fio, t.position, t.academic_degree, d.name
        FROM teachers t
        JOIN departments d ON t.department_id = d.id
        ORDER BY t.fio
        """
        result = db.execute_query(query)
        if result:
            self.populate_table(self.teachers_table, result)

    def load_study_plans(self):
        """Загрузка учебных планов"""
        query = """
        SELECT sp.id, d.name, g.name, t.fio, sp.semester, 
               CONCAT(sp.hours_lecture, '/', sp.hours_practice)
        FROM study_plans sp
        JOIN disciplines d ON sp.discipline_id = d.id
        JOIN groups g ON sp.group_id = g.id
        LEFT JOIN teachers t ON sp.teacher_id = t.id
        ORDER BY g.name, sp.semester, d.name
        """
        result = db.execute_query(query)
        if result:
            self.populate_table(self.plans_table, result)

    def load_schedule(self):
        """Загрузка расписания"""
        query = """
        SELECT s.id, d.name, g.name, t.fio, c.number, 
               CONCAT(s.start_time, '-', s.end_time), s.week_type
        FROM schedule s
        JOIN disciplines d ON s.discipline_id = d.id
        JOIN groups g ON s.group_id = g.id
        LEFT JOIN teachers t ON s.teacher_id = t.id
        JOIN classrooms c ON s.classroom_id = c.id
        ORDER BY s.start_time, g.name
        """
        result = db.execute_query(query)
        if result:
            self.populate_table(self.schedule_table, result)

    def create_students_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Панель управления
        control_layout = QHBoxLayout()

        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)

        add_btn = QPushButton("Добавить студента")
        add_btn.clicked.connect(self.add_student)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_students)

        control_layout.addWidget(QLabel("Группа:"))
        control_layout.addWidget(self.group_filter)
        control_layout.addWidget(add_btn)
        control_layout.addStretch()
        control_layout.addWidget(refresh_btn)

        layout.addLayout(control_layout)

        # Таблица студентов
        self.students_table = self.create_table([
            "ID", "ФИО", "Зачётная книжка", "Группа", "Статус", "Действия"
        ])
        self.students_table.cellDoubleClicked.connect(self.edit_student)
        layout.addWidget(self.students_table)

        widget.setLayout(layout)
        return widget

    def add_student(self):
        """Добавление нового студента"""
        from widgets.editors import StudentEditor
        editor = StudentEditor(parent=self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.load_students()

    def edit_student(self, row, column):
        """Редактирование студента"""
        if column == 5:  # Колонка "Действия"
            student_id = self.students_table.item(row, 0).text()
            student_fio = self.students_table.item(row, 1).text()
            record_book = self.students_table.item(row, 2).text()
            group_name = self.students_table.item(row, 3).text()
            status = self.students_table.item(row, 4).text() == "Активен"

            # Получаем group_id по имени группы
            query = "SELECT id FROM groups WHERE name = %s"
            result = db.execute_query(query, (group_name,))
            group_id = result[0][0] if result else None

            student_data = (student_id, student_fio, record_book, status, group_id)

            from widgets.editors import StudentEditor
            editor = StudentEditor(student_data, parent=self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                self.load_students()

    def create_reports_tab(self):
        """Вкладка отчетов для сотрудника кафедры"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Группа для генерации отчетов
        reports_group = QGroupBox("Генерация отчетов")
        reports_layout = QVBoxLayout()

        # Кнопки отчетов
        grades_report_btn = QPushButton("Ведомость успеваемости")
        student_rating_btn = QPushButton("Рейтинг студентов")
        classroom_occupancy_btn = QPushButton("Занятость аудиторий")

        grades_report_btn.clicked.connect(self.generate_grades_report)
        student_rating_btn.clicked.connect(self.generate_student_rating)
        classroom_occupancy_btn.clicked.connect(self.generate_classroom_occupancy)

        reports_layout.addWidget(grades_report_btn)
        reports_layout.addWidget(student_rating_btn)
        reports_layout.addWidget(classroom_occupancy_btn)

        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        widget.setLayout(layout)
        return widget

    def generate_grades_report(self):
        """Генерация ведомости успеваемости"""
        from widgets.report_dialogs import GradesReportDialog
        dialog = GradesReportDialog(self)
        dialog.exec()

    def generate_student_rating(self):
        """Генерация рейтинга студентов"""
        from widgets.report_dialogs import StudentRatingDialog
        dialog = StudentRatingDialog(self)
        dialog.exec()

    def generate_classroom_occupancy(self):
        """Генерация отчета по занятости аудиторий - упрощенная версия"""
        try:
            print("🔄 ЗАПУСК ГЕНЕРАЦИИ ОТЧЕТА")

            # Создаем и сохраняем прогресс-диалог
            self._progress = QProgressDialog(
                "Генерация отчета по занятости аудиторий...",
                "Отмена", 0, 0, self
            )
            self._progress.setWindowTitle("Пожалуйста, подождите")
            self._progress.setWindowModality(Qt.WindowModality.WindowModal)
            self._progress.setFixedSize(400, 120)
            self._progress.show()

            # Запускаем в основном потоке с небольшой задержкой
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self._generate_directly)

        except Exception as e:
            print(f"💥 Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить генерацию: {str(e)}")

    def _generate_directly(self):
        """Прямая генерация в основном потоке"""
        try:
            from services.report_service import DocumentGenerator

            print("🎯 Начинаем генерацию отчета...")
            file_path = DocumentGenerator.generate_classroom_occupancy_report()

            # Закрываем прогресс-диалог
            if hasattr(self, '_progress'):
                self._progress.close()
                del self._progress

            if file_path:
                print(f"✅ Отчет создан: {file_path}")
                reply = QMessageBox.question(
                    self,
                    "✅ Отчет сгенерирован",
                    "Отчет по занятости аудиторий успешно сгенерирован. Хотите открыть файл?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.open_file(file_path)
            else:
                QMessageBox.critical(self, "❌ Ошибка", "Не удалось сгенерировать отчет")

        except Exception as e:
            if hasattr(self, '_progress'):
                self._progress.close()
                del self._progress

            print(f"💥 Ошибка при генерации: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{str(e)}")

    def on_report_generated(self, file_path, progress, report_name):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "Отчет сгенерирован",
            f"{report_name} успешно сгенерирован. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать отчет: {error}")

    def open_file(self, file_path):
        """Открытие сгенерированного файла"""
        try:
            import os
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.information(
                self,
                "Файл сохранен",
                f"Файл сохранен по пути: {file_path}\n\nОшибка при открытии: {str(e)}"
            )


class TeacherPanel(BasePanel):
    """Панель преподавателя"""

    def __init__(self, teacher_id):
        print(f"🎯 ВХОД В TeacherPanel.__init__ с teacher_id: {teacher_id}")
        self.teacher_id = teacher_id
        print(f"✅ teacher_id установлен: {self.teacher_id}")
        super().__init__()
        print(f"✅ TeacherPanel.__init__ завершен")

    def setup_ui(self):
        print(f"🔄 ВХОД В TeacherPanel.setup_ui")
        super().setup_ui()
        print(f"✅ BasePanel.setup_ui завершен")

        title = QLabel("Панель преподавателя")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(title)
        print(f"✅ Заголовок добавлен")

        tabs = QTabWidget()
        print(f"✅ QTabWidget создан")

        # Мои дисциплины
        disciplines_tab = self.create_disciplines_tab()
        tabs.addTab(disciplines_tab, "📚 Мои дисциплины")
        print(f"✅ Вкладка дисциплин создана")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Моё расписание")
        print(f"✅ Вкладка расписания создана")

        # Успеваемость
        grades_tab = self.create_grades_tab()
        tabs.addTab(grades_tab, "🎯 Успеваемость")
        print(f"✅ Вкладка успеваемости создана")

        # Нагрузка
        workload_tab = self.create_workload_tab()
        tabs.addTab(workload_tab, "📈 Нагрузка")
        print(f"✅ Вкладка нагрузки создана")

        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")
        print(f"✅ Вкладка отчетов создана")

        self.layout.addWidget(tabs)
        print(f"✅ Табы добавлены в layout")

        # Загружаем данные при инициализации
        self.load_initial_data()
        print(f"✅ TeacherPanel.setup_ui завершен успешно")

    def load_initial_data(self):
        """Загрузка начальных данных"""
        try:
            print(f"Загрузка данных для преподавателя ID: {self.teacher_id}")
            self.load_teacher_disciplines()
            self.load_teacher_schedule()
            self.load_workload()
            self.load_disciplines_for_grading()
            # Не загружаем студентов здесь, т.к. нужна выбранная дисциплина
        except Exception as e:
            print(f"Ошибка при загрузке данных преподавателя: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def create_disciplines_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_teacher_disciplines)
        layout.addWidget(refresh_btn)

        self.disciplines_table = self.create_table([
            "Дисциплина", "Группа", "Семестр", "Часы (лек/пр)"
        ])
        layout.addWidget(self.disciplines_table)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_teacher_schedule)
        layout.addWidget(refresh_btn)

        self.schedule_table = self.create_table([
            "День", "Время", "Дисциплина", "Группа", "Аудитория", "Тип недели"
        ])
        layout.addWidget(self.schedule_table)

        widget.setLayout(layout)
        return widget

    def create_workload_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_workload)
        layout.addWidget(refresh_btn)

        # Статистика нагрузки
        stats_layout = QFormLayout()

        self.total_hours_label = QLabel("0")
        self.lecture_hours_label = QLabel("0")
        self.practice_hours_label = QLabel("0")
        self.groups_count_label = QLabel("0")

        stats_layout.addRow("Общее количество часов:", self.total_hours_label)
        stats_layout.addRow("Лекционные часы:", self.lecture_hours_label)
        stats_layout.addRow("Практические часы:", self.practice_hours_label)
        stats_layout.addRow("Количество групп:", self.groups_count_label)

        layout.addLayout(stats_layout)

        # Детальная таблица нагрузки
        self.workload_table = self.create_table([
            "Дисциплина", "Группа", "Лекции (ч)", "Практика (ч)", "Всего (ч)"
        ])
        layout.addWidget(self.workload_table)

        widget.setLayout(layout)
        return widget

    def load_teacher_disciplines(self):
        """Загрузка дисциплин преподавателя"""
        try:
            query = """
            SELECT d.name, g.name, sp.semester, 
                   CONCAT(sp.hours_lecture, '/', sp.hours_practice)
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s
            ORDER BY g.name, sp.semester
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.populate_table(self.disciplines_table, result)
            else:
                self.disciplines_table.setRowCount(0)
        except Exception as e:
            print(f"Ошибка при загрузке дисциплин: {e}")

    def load_teacher_schedule(self):
        """Загрузка расписания преподавателя"""
        try:
            query = """
            SELECT TO_CHAR(s.start_time, 'Day'), 
                   CONCAT(TO_CHAR(s.start_time, 'HH24:MI'), '-', TO_CHAR(s.end_time, 'HH24:MI')),
                   d.name, g.name, c.number, s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            JOIN groups g ON s.group_id = g.id
            JOIN classrooms c ON s.classroom_id = c.id
            WHERE s.teacher_id = %s
            ORDER BY s.start_time
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.populate_table(self.schedule_table, result)
            else:
                self.schedule_table.setRowCount(0)
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")

    def load_workload(self):
        """Загрузка нагрузки преподавателя"""
        try:
            # Общая статистика
            query = """
            SELECT COALESCE(SUM(hours_lecture + hours_practice), 0),
                   COALESCE(SUM(hours_lecture), 0),
                   COALESCE(SUM(hours_practice), 0),
                   COUNT(DISTINCT group_id)
            FROM study_plans
            WHERE teacher_id = %s
            """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                total, lecture, practice, groups = result[0]
                self.total_hours_label.setText(str(total))
                self.lecture_hours_label.setText(str(lecture))
                self.practice_hours_label.setText(str(practice))
                self.groups_count_label.setText(str(groups))

            # Детальная нагрузка
            detail_query = """
            SELECT d.name, g.name, sp.hours_lecture, sp.hours_practice,
                   (sp.hours_lecture + sp.hours_practice)
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s
            ORDER BY g.name, d.name
            """
            detail_result = db.execute_query(detail_query, (self.teacher_id,))
            if detail_result:
                self.populate_table(self.workload_table, detail_result)
            else:
                self.workload_table.setRowCount(0)

        except Exception as e:
            print(f"Ошибка при загрузке нагрузки: {e}")

    def create_grades_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()

        self.grade_group_filter = QComboBox()
        self.grade_discipline_filter = QComboBox()

        self.grade_discipline_filter.currentIndexChanged.connect(self.on_discipline_changed)

        filter_layout.addWidget(QLabel("Дисциплина:"))
        filter_layout.addWidget(self.grade_discipline_filter)
        filter_layout.addWidget(QLabel("Группа:"))
        filter_layout.addWidget(self.grade_group_filter)
        filter_layout.addStretch()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_students_for_grading)

        filter_layout.addWidget(refresh_btn)
        layout.addLayout(filter_layout)

        # Таблица студентов для выставления оценок
        self.grades_table = self.create_table([
            "ID", "Студент", "Зачётная книжка", "Текущая оценка", "Действия"
        ])
        self.grades_table.cellDoubleClicked.connect(self.edit_grade)
        layout.addWidget(self.grades_table)

        widget.setLayout(layout)
        return widget

    def edit_grade(self, row, column):
        """Редактирование оценки студента"""
        if column == 4:  # Колонка "Действия"
            student_id = self.grades_table.item(row, 0).text()
            student_fio = self.grades_table.item(row, 1).text()
            record_book = self.grades_table.item(row, 2).text()
            current_grade = self.grades_table.item(row, 3).text()

            student_data = (student_id, student_fio, record_book)

            # Получаем study_plan_id
            discipline_id = self.grade_discipline_filter.currentData()
            group_id = self.grade_group_filter.currentData()

            query = """
            SELECT id FROM study_plans 
            WHERE discipline_id = %s AND group_id = %s AND teacher_id = %s
            """
            result = db.execute_query(query, (discipline_id, group_id, self.teacher_id))
            study_plan_id = result[0][0] if result else None

            # Проверяем есть ли существующая оценка
            existing_grade = None
            if current_grade != "Нет оценки":
                query = """
                SELECT id, student_id, grade, type, exam_date 
                FROM grades 
                WHERE student_id = %s AND study_plan_id = %s
                """
                result = db.execute_query(query, (student_id, study_plan_id))
                if result:
                    existing_grade = result[0]

            from widgets.editors import GradeEditor
            editor = GradeEditor(student_data, study_plan_id, existing_grade, parent=self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                self.load_students_for_grading()


    def create_reports_tab(self):
        """Вкладка отчетов для преподавателя"""
        widget = QWidget()
        layout = QVBoxLayout()

        reports_group = QGroupBox("Генерация отчетов")
        reports_layout = QVBoxLayout()

        workload_report_btn = QPushButton("Отчет по нагрузке")
        workload_report_btn.clicked.connect(self.generate_workload_report)

        reports_layout.addWidget(workload_report_btn)
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        widget.setLayout(layout)
        return widget

    def generate_workload_report(self):
        """Генерация отчета по нагрузке"""
        try:
            print(f"🔍 Генерация отчета по нагрузке для teacher_id: {self.teacher_id}")

            if not hasattr(self, 'teacher_id') or not self.teacher_id:
                QMessageBox.warning(self, "Ошибка", "ID преподавателя не найден")
                return

            progress = QProgressDialog("Генерация отчета по нагрузке...", "Отмена", 0, 0, self)
            progress.setWindowTitle("Пожалуйста, подождите")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setStyleSheet("""
                QProgressDialog {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            progress.show()

            # Запуск в отдельном потоке
            self.thread = ReportGenerationThread('workload_report', teacher_id=self.teacher_id)
            self.thread.finished.connect(lambda path: self.on_report_generated(path, progress, "Отчет по нагрузке"))
            self.thread.error.connect(lambda error: self.on_report_error(error, progress))
            self.thread.start()

        except Exception as e:
            print(f"💥 Ошибка при запуске генерации отчета: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить генерацию отчета: {e}")

    def on_report_generated(self, file_path, progress, report_name):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "✅ Отчет сгенерирован",
            f"{report_name} успешно сгенерирован. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        print(f"💥 Ошибка генерации отчета: {error}")
        QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{error}")

    def open_file(self, file_path):
        """Открытие сгенерированного файла"""
        try:
            import os
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.information(
                self,
                "📁 Файл сохранен",
                f"Файл сохранен по пути: {file_path}\n\nОшибка при открытии: {str(e)}"
            )


    def load_disciplines_for_grading(self):
        """Загрузка дисциплин преподавателя для выставления оценок"""
        try:
            query = """
               SELECT DISTINCT d.id, d.name
               FROM study_plans sp
               JOIN disciplines d ON sp.discipline_id = d.id
               WHERE sp.teacher_id = %s
               ORDER BY d.name
               """
            result = db.execute_query(query, (self.teacher_id,))
            if result:
                self.grade_discipline_filter.clear()
                self.grade_discipline_filter.addItem("Выберите дисциплину", None)
                for discipline_id, discipline_name in result:
                    self.grade_discipline_filter.addItem(discipline_name, discipline_id)
            else:
                print("Нет дисциплин для преподавателя")
        except Exception as e:
            print(f"Ошибка при загрузке дисциплин: {e}")

    def load_groups_for_grading(self):
        """Загрузка групп для выбранной дисциплины"""
        try:
            discipline_id = self.grade_discipline_filter.currentData()
            if not discipline_id:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Сначала выберите дисциплину", None)
                return

            query = """
            SELECT DISTINCT g.id, g.name
            FROM study_plans sp
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s AND sp.discipline_id = %s
            ORDER BY g.name
            """
            result = db.execute_query(query, (self.teacher_id, discipline_id))
            if result:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Все группы", None)
                for group_id, group_name in result:
                    self.grade_group_filter.addItem(group_name, group_id)
            else:
                self.grade_group_filter.clear()
                self.grade_group_filter.addItem("Нет групп для этой дисциплины", None)
        except Exception as e:
            print(f"Ошибка при загрузке групп: {e}")

    def on_discipline_changed(self):
        """Обработчик изменения выбранной дисциплины"""
        self.load_groups_for_grading()
        # Очищаем таблицу студентов при смене дисциплины
        self.grades_table.setRowCount(0)

    def load_students_for_grading(self):
        """Загрузка студентов для выставления оценок"""
        try:
            discipline_id = self.grade_discipline_filter.currentData()
            group_id = self.grade_group_filter.currentData()

            if not discipline_id:
                QMessageBox.warning(self, "Ошибка", "Выберите дисциплину")
                return

            query = """
               SELECT s.id, s.fio, s.record_book_id, 
                      COALESCE(g.grade, 'Нет оценки') as current_grade
               FROM students s
               JOIN groups gr ON s.group_id = gr.id
               JOIN study_plans sp ON sp.group_id = gr.id AND sp.discipline_id = %s AND sp.teacher_id = %s
               LEFT JOIN grades g ON g.student_id = s.id AND g.study_plan_id = sp.id
               WHERE (%s IS NULL OR s.group_id = %s) AND s.status = true
               ORDER BY s.fio
               """
            result = db.execute_query(query, (discipline_id, self.teacher_id, group_id, group_id))

            if result:
                self.populate_table(self.grades_table, result)
            else:
                self.grades_table.setRowCount(0)
                QMessageBox.information(self, "Информация", "Нет студентов для выбранных параметров")

        except Exception as e:
            print(f"Ошибка при загрузке студентов: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить студентов: {str(e)}")


class StudentPanel(BasePanel):
    """Панель студента"""

    def __init__(self, student_id):
        self.student_id = student_id  # Сначала устанавливаем student_id
        print(f"Создана StudentPanel с student_id: {student_id}")
        super().__init__()  # Затем вызываем родительский конструктор

    def setup_ui(self):
        super().setup_ui()

        title = QLabel("Панель студента")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        self.layout.addWidget(title)

        tabs = QTabWidget()

        # Успеваемость
        grades_tab = self.create_grades_tab()
        tabs.addTab(grades_tab, "📖 Успеваемость")

        # Расписание
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 Расписание")

        # Зачётная книжка
        record_book_tab = self.create_record_book_tab()
        tabs.addTab(record_book_tab, "📚 Зачётная книжка")

        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📊 Отчеты")

        self.layout.addWidget(tabs)

        # Загружаем данные при инициализации
        self.load_initial_data()

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.load_student_grades()
        self.load_student_schedule()
        self.load_record_book()

    def create_grades_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_student_grades)
        layout.addWidget(refresh_btn)

        self.grades_table = self.create_table([
            "Дисциплина", "Оценка", "Тип контроля", "Дата", "Преподаватель"
        ])
        layout.addWidget(self.grades_table)

        # Статистика
        stats_group = QGroupBox("Статистика успеваемости")
        stats_layout = QFormLayout()

        self.avg_grade_label = QLabel("0.0")
        self.total_subjects_label = QLabel("0")
        self.completed_label = QLabel("0")

        stats_layout.addRow("Средний балл:", self.avg_grade_label)
        stats_layout.addRow("Всего дисциплин:", self.total_subjects_label)
        stats_layout.addRow("Сдано дисциплин:", self.completed_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_student_schedule)
        layout.addWidget(refresh_btn)

        self.schedule_table = self.create_table([
            "День", "Время", "Дисциплина", "Преподаватель", "Аудитория", "Тип недели"
        ])
        layout.addWidget(self.schedule_table)

        widget.setLayout(layout)
        return widget

    def create_record_book_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_record_book)
        layout.addWidget(refresh_btn)

        self.record_book_table = self.create_table([
            "Семестр", "Дисциплина", "Оценка", "Тип", "Дата", "Преподаватель"
        ])
        layout.addWidget(self.record_book_table)

        widget.setLayout(layout)
        return widget

    def load_student_grades(self):
        """Загрузка оценок студента"""
        try:
            print(f"Загрузка оценок для студента ID: {self.student_id}")
            query = """
            SELECT d.name, g.grade, g.type, g.exam_date, t.fio
            FROM grades g
            JOIN study_plans sp ON g.study_plan_id = sp.id
            JOIN disciplines d ON sp.discipline_id = d.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            WHERE g.student_id = %s
            ORDER BY g.exam_date DESC
            """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.grades_table, result)

                # Расчет статистики
                numeric_grades = []
                for row in result:
                    grade = row[1]
                    if grade and grade.isdigit():
                        numeric_grades.append(int(grade))

                if numeric_grades:
                    avg_grade = sum(numeric_grades) / len(numeric_grades)
                    self.avg_grade_label.setText(f"{avg_grade:.2f}")
                else:
                    self.avg_grade_label.setText("0.0")

                self.total_subjects_label.setText(str(len(set([r[0] for r in result]))))
                self.completed_label.setText(str(len([r for r in result if r[1] in ['зачёт', '5', '4', '3']])))
            else:
                print("Нет данных об оценках")
                self.avg_grade_label.setText("0.0")
                self.total_subjects_label.setText("0")
                self.completed_label.setText("0")

        except Exception as e:
            print(f"Ошибка при загрузке оценок: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить оценки: {str(e)}")

    def load_student_schedule(self):
        """Загрузка расписания студента"""
        try:
            print(f"Загрузка расписания для студента ID: {self.student_id}")
            query = """
            SELECT TO_CHAR(s.start_time, 'Day'), 
                   CONCAT(s.start_time, '-', s.end_time),
                   d.name, t.fio, c.number, s.week_type
            FROM schedule s
            JOIN disciplines d ON s.discipline_id = d.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            JOIN classrooms c ON s.classroom_id = c.id
            JOIN groups g ON s.group_id = g.id
            JOIN students st ON st.group_id = g.id
            WHERE st.id = %s
            ORDER BY s.start_time
            """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.schedule_table, result)
            else:
                print("Нет данных о расписании")
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить расписание: {str(e)}")

    def load_record_book(self):
        """Загрузка зачётной книжки"""
        try:
            print(f"Загрузка зачётной книжки для студента ID: {self.student_id}")
            query = """
               SELECT sp.semester, d.name, g.grade, g.type, g.exam_date, t.fio
               FROM grades g
               JOIN study_plans sp ON g.study_plan_id = sp.id
               JOIN disciplines d ON sp.discipline_id = d.id
               LEFT JOIN teachers t ON sp.teacher_id = t.id
               WHERE g.student_id = %s
               ORDER BY sp.semester, d.name
               """
            result = db.execute_query(query, (self.student_id,))
            if result:
                self.populate_table(self.record_book_table, result)
            else:
                print("Нет данных для зачётной книжки")
        except Exception as e:
            print(f"Ошибка при загрузке зачётной книжки: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить зачётную книжку: {str(e)}")

    def create_reports_tab(self):
        """Вкладка отчетов для студента"""
        widget = QWidget()
        layout = QVBoxLayout()

        reports_group = QGroupBox("Генерация отчетов")
        reports_layout = QVBoxLayout()

        record_book_btn = QPushButton("Зачётная книжка")
        record_book_btn.clicked.connect(self.generate_record_book)

        reports_layout.addWidget(record_book_btn)
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)

        widget.setLayout(layout)
        return widget

    def generate_record_book(self):
        """Генерация зачётной книжки"""
        from widgets.report_dialogs import RecordBookDialog
        dialog = RecordBookDialog(self)
        # Автоматически выбираем текущего студента
        for i in range(dialog.student_combo.count()):
            if dialog.student_combo.itemData(i) == self.student_id:
                dialog.student_combo.setCurrentIndex(i)
                break
        dialog.exec()