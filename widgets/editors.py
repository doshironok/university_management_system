from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QComboBox, QMessageBox,
                             QDialog, QFormLayout, QDateEdit, QSpinBox,
                             QCheckBox, QGroupBox, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QDate
from database import db
from services.data_service import DataService
from utils.helpers import apply_dialog_style


class StudentEditor(QDialog):
    """Диалог редактирования студента"""

    def __init__(self, student_data=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.student_data = student_data
        self.setup_ui()
        self.load_groups()

    def setup_ui(self):
        self.setWindowTitle("Редактирование студента" if self.student_data else "Добавление студента")
        self.setFixedSize(400, 350)

        layout = QFormLayout()

        # Поля формы
        self.fio_input = QLineEdit()
        self.record_book_input = QLineEdit()
        self.group_combo = QComboBox()
        self.status_checkbox = QCheckBox("Активный студент")
        self.status_checkbox.setChecked(True)

        # Заполняем данные если редактируем
        if self.student_data:
            self.fio_input.setText(self.student_data[1] if self.student_data[1] else "")
            self.record_book_input.setText(self.student_data[2] if self.student_data[2] else "")
            if len(self.student_data) > 4:
                self.status_checkbox.setChecked(bool(self.student_data[4]))

        layout.addRow("ФИО:", self.fio_input)
        layout.addRow("Номер зачётной книжки:", self.record_book_input)
        layout.addRow("Группа:", self.group_combo)
        layout.addRow(self.status_checkbox)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save_student)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)

        self.setLayout(layout)

    def load_groups(self):
        """Загрузка списка групп"""
        try:
            query = "SELECT id, name FROM groups ORDER BY name"
            result = db.execute_query(query)
            if result:
                for group_id, group_name in result:
                    self.group_combo.addItem(group_name, group_id)

                # Устанавливаем текущую группу если редактируем
                if self.student_data and len(self.student_data) > 5:
                    current_group_id = self.student_data[5]  # group_id из данных студента
                    if current_group_id:
                        index = self.group_combo.findData(current_group_id)
                        if index >= 0:
                            self.group_combo.setCurrentIndex(index)
        except Exception as e:
            print(f"Ошибка при загрузке групп: {e}")

    def save_student(self):
        """Сохранение студента"""
        fio = self.fio_input.text().strip()
        record_book = self.record_book_input.text().strip()
        group_id = self.group_combo.currentData()
        status = self.status_checkbox.isChecked()

        if not fio or not record_book or not group_id:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        try:
            if self.student_data and self.student_data[0]:
                # Обновление существующего студента
                query = """
                UPDATE students 
                SET fio = %s, record_book_id = %s, group_id = %s, status = %s
                WHERE id = %s
                """
                success = db.execute_query(query, (fio, record_book, group_id, status, self.student_data[0]), fetch=False)
                message = "Данные студента обновлены"
            else:
                # Добавление нового студента
                query = """
                INSERT INTO students (fio, record_book_id, group_id, status)
                VALUES (%s, %s, %s, %s)
                """
                success = db.execute_query(query, (fio, record_book, group_id, status), fetch=False)
                message = "Студент добавлен"

            if success:
                QMessageBox.information(self, "Успех", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")

        except Exception as e:
            print(f"Ошибка при сохранении студента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

class GradeEditor(QDialog):
    """Диалог выставления/редактирования оценки"""

    def __init__(self, student_data, study_plan_id, existing_grade=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.student_data = student_data          # (id, fio, record_book)
        self.study_plan_id = study_plan_id      # int
        self.existing_grade = existing_grade    # кортеж из БД или None
        print(f"🔍 [DEBUG] Создание GradeEditor: student_data={student_data}, study_plan_id={study_plan_id}, existing_grade={existing_grade}")
        self.setup_ui()

    def setup_ui(self):
        title = "Редактирование оценки" if self.existing_grade else "Выставление оценки"
        self.setWindowTitle(title)
        self.setFixedSize(450, 320)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setObjectName("dialog_frame")
        frame_layout = QFormLayout()
        frame_layout.setContentsMargins(40, 40, 40, 40)

        student_info = QLabel(f"<b>Студент:</b> {self.student_data[1]}<br>"
                              f"<b>Зачётная книжка:</b> {self.student_data[2]}")
        student_info.setStyleSheet("font-size: 14px; margin-bottom: 15px;")
        frame_layout.addRow(student_info)

        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["5", "4", "3", "2", "зачёт", "незачёт"])
        self.type_combo = QComboBox()
        self.type_combo.addItems(["экзамен", "зачёт", "курсовая работа", "практическая работа"])
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        if self.existing_grade:
            self.grade_combo.setCurrentText(self.existing_grade[2])
            self.type_combo.setCurrentText(self.existing_grade[3])
            if self.existing_grade and self.existing_grade[4]:
                # Теперь exam_date — это всегда строка в формате 'YYYY-MM-DD'
                self.date_edit.setDate(QDate.fromString(self.existing_grade[4], "yyyy-MM-dd"))

        frame_layout.addRow("Оценка:", self.grade_combo)
        frame_layout.addRow("Тип контроля:", self.type_combo)
        frame_layout.addRow("Дата:", self.date_edit)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        delete_btn = QPushButton("Удалить") if self.existing_grade else None
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save_grade)
        cancel_btn.clicked.connect(self.reject)
        if delete_btn:
            delete_btn.clicked.connect(self.delete_grade)

        button_layout.addWidget(save_btn)
        if delete_btn:
            button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        frame_layout.addRow(button_layout)

        frame.setLayout(frame_layout)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def save_grade(self):
        """Сохранение оценки"""
        grade = self.grade_combo.currentText()
        grade_type = self.type_combo.currentText()
        exam_date = self.date_edit.date().toString("yyyy-MM-dd")

        print(f"💾 [DEBUG] Сохранение оценки: student_id={self.student_data[0]}, study_plan_id={self.study_plan_id}, grade='{grade}', type='{grade_type}', date='{exam_date}'")

        try:
            if self.existing_grade:
                # Обновление существующей оценки
                delete_query = "DELETE FROM grades WHERE id = %s"
                db.execute_query(delete_query, (self.existing_grade[0],), fetch=False)

            # Добавляем новую
            insert_query = """
            INSERT INTO grades (student_id, study_plan_id, grade, exam_date, type)
            VALUES (%s, %s, %s, %s, %s)
            """
            success = db.execute_query(
                insert_query,
                (self.student_data[0], self.study_plan_id, grade, exam_date, grade_type),
                fetch=False
            )

            if success:
                print("✅ [DEBUG] Оценка сохранена успешно")
                QMessageBox.information(self, "Успех", "Оценка сохранена")
                self.accept()
            else:
                print("❌ [DEBUG] Не удалось сохранить оценку")
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить оценку")
        except Exception as e:
            print(f"💥 [DEBUG] Исключение при сохранении: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")


class ScheduleEditor(QDialog):
    def __init__(self, schedule_data=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.schedule_data = schedule_data  # (id, discipline_id, classroom_id, teacher_id, group_id, start, end, week_type)
        self.setup_ui()
        self.load_initial_data()
        if self.schedule_data:
            self.setWindowTitle("Редактирование занятия")
            self.populate_from_data()

    def populate_from_data(self):
        _, disc_id, class_id, teacher_id, group_id, start, end, week_type = self.schedule_data
        self.discipline_combo.setCurrentIndex(self.discipline_combo.findData(disc_id))
        self.classroom_combo.setCurrentIndex(self.classroom_combo.findData(class_id))
        self.teacher_combo.setCurrentIndex(self.teacher_combo.findData(teacher_id))
        self.group_combo.setCurrentIndex(self.group_combo.findData(group_id))
        self.start_time_edit.setText(start)
        self.end_time_edit.setText(end)
        idx = self.week_type_combo.findText(week_type)
        if idx >= 0:
            self.week_type_combo.setCurrentIndex(idx)

    def setup_ui(self):
        self.setWindowTitle("Добавление занятия в расписание")
        self.setFixedSize(500, 400)
        layout = QFormLayout()
        # Выпадающие списки
        self.discipline_combo = QComboBox()
        self.classroom_combo = QComboBox()
        self.teacher_combo = QComboBox()
        self.group_combo = QComboBox()
        # Поля времени
        time_layout = QHBoxLayout()
        self.start_time_edit = QLineEdit()
        self.start_time_edit.setPlaceholderText("09:00")
        self.end_time_edit = QLineEdit()
        self.end_time_edit.setPlaceholderText("10:30")
        time_layout.addWidget(QLabel("С:"))
        time_layout.addWidget(self.start_time_edit)
        time_layout.addWidget(QLabel("До:"))
        time_layout.addWidget(self.end_time_edit)
        # Тип недели
        self.week_type_combo = QComboBox()
        self.week_type_combo.addItems(["каждую", "чётная", "нечётная"])
        layout.addRow("Дисциплина:", self.discipline_combo)
        layout.addRow("Аудитория:", self.classroom_combo)
        layout.addRow("Преподаватель:", self.teacher_combo)
        layout.addRow("Группа:", self.group_combo)
        layout.addRow("Время:", time_layout)
        layout.addRow("Тип недели:", self.week_type_combo)
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        delete_btn = QPushButton("Удалить")  # ← НОВАЯ КНОПКА
        check_btn = QPushButton("Проверить доступность")
        save_btn.clicked.connect(self.save_schedule)
        delete_btn.clicked.connect(self.delete_schedule)
        check_btn.clicked.connect(self.check_availability)
        # Увеличиваем размер кнопки «Проверить доступность»
        check_btn.setStyleSheet("""
               QPushButton {
                   background-color: #27ae60;
                   color: white;
                   border: none;
                   border-radius: 6px;
                   padding: 10px 20px;
                   font-size: 13px;
                   font-weight: bold;
                   min-width: 180px;
               }
               QPushButton:hover { background-color: #2ecc71; }
               QPushButton:pressed { background-color: #22a7f0; }
           """)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(check_btn)
        layout.addRow(button_layout)
        self.setLayout(layout)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        # Загрузка дисциплин
        disciplines = db.execute_query("SELECT id, name FROM disciplines ORDER BY name")
        for disc_id, disc_name in disciplines:
            self.discipline_combo.addItem(disc_name, disc_id)
        # Загрузка аудиторий
        classrooms = db.execute_query("SELECT id, number FROM classrooms ORDER BY number")
        for class_id, class_num in classrooms:
            self.classroom_combo.addItem(class_num, class_id)
        # Загрузка преподавателей
        teachers = db.execute_query("SELECT id, fio FROM teachers ORDER BY fio")
        for teacher_id, teacher_fio in teachers:
            self.teacher_combo.addItem(teacher_fio, teacher_id)
        # Загрузка групп
        groups = db.execute_query("SELECT id, name FROM groups ORDER BY name")
        for group_id, group_name in groups:
            self.group_combo.addItem(group_name, group_id)

    def check_availability(self):
        """Проверка доступности аудитории"""
        classroom_id = self.classroom_combo.currentData()
        start_time = self.start_time_edit.text()
        end_time = self.end_time_edit.text()
        week_type = self.week_type_combo.currentText()
        if not all([classroom_id, start_time, end_time]):
            QMessageBox.warning(self, "Ошибка", "Заполните время и выберите аудиторию")
            return
        try:
            is_available = DataService.check_classroom_availability(
                classroom_id, start_time, end_time, week_type
            )
            if is_available:
                QMessageBox.information(self, "Проверка", "Аудитория свободна в указанное время")
            else:
                QMessageBox.warning(self, "Проверка", "Аудитория занята в указанное время")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке: {str(e)}")

    def save_schedule(self):
        """Сохранение занятия в расписание"""
        discipline_id = self.discipline_combo.currentData()
        classroom_id = self.classroom_combo.currentData()
        teacher_id = self.teacher_combo.currentData()
        group_id = self.group_combo.currentData()
        start_time = self.start_time_edit.text()
        end_time = self.end_time_edit.text()
        week_type = self.week_type_combo.currentText()
        if not all([discipline_id, classroom_id, teacher_id, group_id, start_time, end_time]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        try:
            if self.schedule_data:
                # Обновление
                query = """
                UPDATE schedule 
                SET discipline_id = %s, classroom_id = %s, teacher_id = %s,
                    group_id = %s, start_time = %s, end_time = %s, week_type = %s
                WHERE id = %s
                """
                params = (discipline_id, classroom_id, teacher_id, group_id, start_time, end_time, week_type, self.schedule_data[0])
                success = db.execute_query(query, params, fetch=False)
                message = "Занятие обновлено"
            else:
                # Добавление
                query = """
                INSERT INTO schedule (discipline_id, classroom_id, teacher_id, group_id, start_time, end_time, week_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (discipline_id, classroom_id, teacher_id, group_id, start_time, end_time, week_type)
                success = db.execute_query(query, params, fetch=False)
                message = "Занятие добавлено"

            if success:
                QMessageBox.information(self, "Успех", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить занятие")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def delete_schedule(self):
        """Удаление занятия из расписания"""
        if not self.schedule_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для удаления")
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить занятие?\n"
            f"Дисциплина: {self.discipline_combo.currentText()}\n"
            f"Группа: {self.group_combo.currentText()}\n"
            f"Время: {self.start_time_edit.text()} - {self.end_time_edit.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM schedule WHERE id = %s"
                success = db.execute_query(query, (self.schedule_data[0],), fetch=False)
                if success:
                    QMessageBox.information(self, "Успех", "Занятие удалено")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить занятие")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")


class DisciplineEditor(QDialog):
    """Редактор дисциплин"""

    def __init__(self, discipline_data=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.discipline_data = discipline_data
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Редактор дисциплины")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.department_combo = QComboBox()

        # Заполняем кафедры
        departments = db.execute_query("SELECT id, name FROM departments ORDER BY name")
        if departments:
            for dept_id, dept_name in departments:
                self.department_combo.addItem(dept_name, dept_id)

        if self.discipline_data:
            self.name_input.setText(self.discipline_data[1])
            # Устанавливаем выбранную кафедру
            index = self.department_combo.findData(self.discipline_data[2])
            if index >= 0:
                self.department_combo.setCurrentIndex(index)

        form_layout.addRow("Название дисциплины:", self.name_input)
        form_layout.addRow("Кафедра:", self.department_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save_discipline)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_discipline(self):
        name = self.name_input.text().strip()
        department_id = self.department_combo.currentData()

        if not name or not department_id:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            if self.discipline_data:
                # Редактирование
                query = "UPDATE disciplines SET name = %s, department_id = %s WHERE id = %s"
                success = db.execute_query(query, (name, department_id, self.discipline_data[0]), fetch=False)
            else:
                # Добавление
                query = "INSERT INTO disciplines (name, department_id) VALUES (%s, %s)"
                success = db.execute_query(query, (name, department_id), fetch=False)

            if success:
                QMessageBox.information(self, "Успех", "Дисциплина сохранена")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить дисциплину")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")


class StudyPlanEditor(QDialog):
    def __init__(self, plan_data=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.plan_data = plan_data  # (id, discipline_id, group_id, teacher_id, semester, lecture, practice)
        self.setup_ui()
        self.load_combobox_data()
        if self.plan_data:
            self.setWindowTitle("Редактирование учебного плана")
            self.populate_from_data()

    def populate_from_data(self):
        """Заполнить форму данными при редактировании"""
        _, disc_id, group_id, teacher_id, sem, lect, pract = self.plan_data
        self.discipline_combo.setCurrentIndex(self.discipline_combo.findData(disc_id))
        self.group_combo.setCurrentIndex(self.group_combo.findData(group_id))
        self.teacher_combo.setCurrentIndex(self.teacher_combo.findData(teacher_id))
        self.semester_spin.setValue(sem)
        self.lecture_hours_spin.setValue(lect)
        self.practice_hours_spin.setValue(pract)

    def setup_ui(self):
        self.setWindowTitle("Добавление учебного плана")
        self.setFixedSize(500, 400)
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        # Поля формы
        self.discipline_combo = QComboBox()
        self.group_combo = QComboBox()
        self.teacher_combo = QComboBox()
        self.semester_spin = QSpinBox()
        self.lecture_hours_spin = QSpinBox()
        self.practice_hours_spin = QSpinBox()
        # Настройка спинбоксов
        self.semester_spin.setRange(1, 12)
        self.lecture_hours_spin.setRange(0, 200)
        self.practice_hours_spin.setRange(0, 200)
        # Загрузка данных
        self.load_combobox_data()
        form_layout.addRow("Дисциплина:", self.discipline_combo)
        form_layout.addRow("Группа:", self.group_combo)
        form_layout.addRow("Преподаватель:", self.teacher_combo)
        form_layout.addRow("Семестр:", self.semester_spin)
        form_layout.addRow("Лекционные часы:", self.lecture_hours_spin)
        form_layout.addRow("Практические часы:", self.practice_hours_spin)
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        delete_btn = QPushButton("Удалить")  # ← НОВАЯ КНОПКА
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self.save_plan)
        delete_btn.clicked.connect(self.delete_plan)  # ← Связь с новым методом
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)  # ← Добавляем рядом с сохранить
        button_layout.addWidget(cancel_btn)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_combobox_data(self):
        """Загрузка данных в комбобоксы"""
        # Дисциплины
        disciplines = db.execute_query("SELECT id, name FROM disciplines ORDER BY name")
        if disciplines:
            for disc_id, disc_name in disciplines:
                self.discipline_combo.addItem(disc_name, disc_id)
        # Группы
        groups = db.execute_query("SELECT id, name FROM groups ORDER BY name")
        if groups:
            for group_id, group_name in groups:
                self.group_combo.addItem(group_name, group_id)
        # Преподаватели
        teachers = db.execute_query("SELECT id, fio FROM teachers ORDER BY fio")
        if teachers:
            for teacher_id, teacher_fio in teachers:
                self.teacher_combo.addItem(teacher_fio, teacher_id)

    def save_plan(self):
        """Сохранение учебного плана с отладочными логами"""
        print("🔍 [DEBUG] Начало save_plan")
        discipline_id = self.discipline_combo.currentData()
        group_id = self.group_combo.currentData()
        teacher_id = self.teacher_combo.currentData()
        semester = self.semester_spin.value()
        lecture_hours = self.lecture_hours_spin.value()
        practice_hours = self.practice_hours_spin.value()

        print(f"📝 [DEBUG] discipline_id = {discipline_id}")
        print(f"📝 [DEBUG] group_id = {group_id}")
        print(f"📝 [DEBUG] teacher_id = {teacher_id}")
        print(f"📝 [DEBUG] semester = {semester}")
        print(f"📝 [DEBUG] lecture_hours = {lecture_hours}")
        print(f"📝 [DEBUG] practice_hours = {practice_hours}")

        if not all([discipline_id, group_id, teacher_id]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            print("❌ [DEBUG] Не заполнены обязательные поля")
            return

        try:
            if self.plan_data:
                # Обновление
                query = """
                UPDATE study_plans 
                SET discipline_id = %s, group_id = %s, teacher_id = %s, 
                    semester = %s, hours_lecture = %s, hours_practice = %s
                WHERE id = %s
                """
                params = (
                discipline_id, group_id, teacher_id, semester, lecture_hours, practice_hours, self.plan_data[0])
                print(f"🔄 [DEBUG] Выполняется UPDATE: {query}")
                print(f"📊 [DEBUG] Параметры: {params}")
            else:
                # Добавление
                query = """
                INSERT INTO study_plans (discipline_id, group_id, teacher_id, semester, hours_lecture, hours_practice)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (discipline_id, group_id, teacher_id, semester, lecture_hours, practice_hours)
                print(f"➕ [DEBUG] Выполняется INSERT: {query}")
                print(f"📊 [DEBUG] Параметры: {params}")

            success = db.execute_query(query, params, fetch=False)
            print(f"✅ [DEBUG] Результат выполнения: {success}")

            if success:
                message = "Учебный план обновлён" if self.plan_data else "Учебный план добавлен"
                QMessageBox.information(self, "Успех", message)
                self.accept()
                print("✅ [DEBUG] Операция завершена успешно")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить учебный план")
                print("❌ [DEBUG] execute_query вернул False")

        except Exception as e:
            print(f"💥 [DEBUG] Исключение в save_plan: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def delete_plan(self):
        """Удаление учебного плана"""
        if not self.plan_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для удаления")
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить учебный план?\n"
            f"Дисциплина: {self.discipline_combo.currentText()}\n"
            f"Группа: {self.group_combo.currentText()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM study_plans WHERE id = %s"
                success = db.execute_query(query, (self.plan_data[0],), fetch=False)
                if success:
                    QMessageBox.information(self, "Успех", "Учебный план удалён")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить учебный план")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

class TeacherEditor(QDialog):
    """Диалог редактирования преподавателя"""

    def __init__(self, teacher_data=None, parent=None):
        super().__init__(parent)
        apply_dialog_style(self)
        self.teacher_data = teacher_data
        self.setup_ui()
        self.load_departments()

    def setup_ui(self):
        self.setWindowTitle("Редактирование преподавателя" if self.teacher_data else "Добавление преподавателя")
        self.setFixedSize(400, 350)

        layout = QFormLayout()

        # Поля формы
        self.fio_input = QLineEdit()
        self.position_input = QLineEdit()
        self.degree_input = QLineEdit()
        self.department_combo = QComboBox()

        # Заполняем данные если редактируем
        if self.teacher_data:
            self.fio_input.setText(self.teacher_data[1])
            self.position_input.setText(self.teacher_data[2])
            self.degree_input.setText(self.teacher_data[3])

        layout.addRow("ФИО:", self.fio_input)
        layout.addRow("Должность:", self.position_input)
        layout.addRow("Учёная степень:", self.degree_input)
        layout.addRow("Кафедра:", self.department_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")

        save_btn.clicked.connect(self.save_teacher)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)

        self.setLayout(layout)

    def load_departments(self):
        """Загрузка списка кафедр"""
        query = "SELECT id, name FROM departments ORDER BY name"
        result = db.execute_query(query)
        if result:
            for dept_id, dept_name in result:
                self.department_combo.addItem(dept_name, dept_id)

            # Устанавливаем текущую кафедру если редактируем
            if self.teacher_data:
                current_dept_id = self.teacher_data[4]  # department_id из данных преподавателя
                index = self.department_combo.findData(current_dept_id)
                if index >= 0:
                    self.department_combo.setCurrentIndex(index)

    def save_teacher(self):
        """Сохранение преподавателя"""
        fio = self.fio_input.text().strip()
        position = self.position_input.text().strip()
        degree = self.degree_input.text().strip()
        department_id = self.department_combo.currentData()

        if not fio or not position or not department_id:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        try:
            if self.teacher_data:
                # Обновление существующего преподавателя
                query = """
                UPDATE teachers 
                SET fio = %s, position = %s, academic_degree = %s, department_id = %s
                WHERE id = %s
                """
                success = db.execute_query(query, (fio, position, degree, department_id, self.teacher_data[0]), fetch=False)
                message = "Данные преподавателя обновлены"
            else:
                # Добавление нового преподавателя
                query = """
                INSERT INTO teachers (fio, position, academic_degree, department_id)
                VALUES (%s, %s, %s, %s)
                """
                success = db.execute_query(query, (fio, position, degree, department_id), fetch=False)
                message = "Преподаватель добавлен"

            if success:
                QMessageBox.information(self, "Успех", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")