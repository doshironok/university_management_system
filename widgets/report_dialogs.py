from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QFormLayout, QMessageBox,
                             QProgressDialog, QFileDialog, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import subprocess
import platform
from database import db
from services.report_service import DocumentGenerator


class ReportGenerationThread(QThread):
    """Поток для генерации отчетов"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, report_type, **kwargs):
        super().__init__()
        self.report_type = report_type
        self.kwargs = kwargs

    def run(self):
        try:
            if self.report_type == 'record_book':
                file_path = DocumentGenerator.generate_student_record_book(self.kwargs['student_id'])
            elif self.report_type == 'grades_report':
                file_path = DocumentGenerator.generate_grades_report(
                    self.kwargs['group_id'], self.kwargs['discipline_id']
                )
            elif self.report_type == 'workload_report':
                file_path = DocumentGenerator.generate_teacher_workload_report(self.kwargs['teacher_id'])
            elif self.report_type == 'classroom_occupancy':
                file_path = DocumentGenerator.generate_classroom_occupancy_report()
            elif self.report_type == 'student_rating':
                file_path = DocumentGenerator.generate_student_rating_report(self.kwargs['group_id'])
            else:
                self.error.emit("Неизвестный тип отчета")
                return

            if file_path:
                self.finished.emit(file_path)
            else:
                self.error.emit("Не удалось сгенерировать отчет")

        except Exception as e:
            self.error.emit(str(e))


class BaseReportDialog(QDialog):
    """Базовый класс для диалогов отчетов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#main_frame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLabel#title {
                color: #2c3e50;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QComboBox {
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background-color: #fafafa;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #3498db;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #3498db;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton#primary_button {
                background-color: #3498db;
                color: white;
            }
            QPushButton#primary_button:hover {
                background-color: #2980b9;
            }
            QPushButton#primary_button:pressed {
                background-color: #21618c;
            }
            QPushButton#secondary_button {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton#secondary_button:hover {
                background-color: #7f8c8d;
            }
            QPushButton#secondary_button:pressed {
                background-color: #6c7b7d;
            }
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def create_main_frame(self):
        """Создает основной фрейм диалога"""
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        return main_frame

    def open_file(self, file_path):
        """Открытие сгенерированного файла"""
        try:
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


class RecordBookDialog(BaseReportDialog):
    """Диалог генерации зачётной книжки"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        self.setWindowTitle("📚 Генерация зачётной книжки")
        self.setFixedSize(450, 250)

        # Главный layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Основной фрейм
        main_frame = self.create_main_frame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("Генерация зачётной книжки")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)

        # Группа формы
        form_group = QGroupBox("Параметры отчета")
        form_layout = QFormLayout()

        self.student_combo = QComboBox()
        form_layout.addRow("🎓 Студент:", self.student_combo)

        form_group.setLayout(form_layout)
        frame_layout.addWidget(form_group)

        # Кнопки
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Сгенерировать")
        generate_btn.setObjectName("primary_button")
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_button")

        generate_btn.clicked.connect(self.generate_report)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(generate_btn)
        button_layout.addWidget(cancel_btn)

        frame_layout.addLayout(button_layout)

        main_frame.setLayout(frame_layout)
        layout.addWidget(main_frame)
        self.setLayout(layout)

    def load_students(self):
        """Загрузка списка студентов"""
        query = """
        SELECT s.id, s.fio, g.name 
        FROM students s 
        JOIN groups g ON s.group_id = g.id 
        WHERE s.status = true 
        ORDER BY g.name, s.fio
        """
        result = db.execute_query(query)
        if result:
            self.student_combo.addItem("Выберите студента", None)
            for student_id, student_fio, group_name in result:
                self.student_combo.addItem(f"{student_fio} ({group_name})", student_id)

    def generate_report(self):
        """Генерация отчета"""
        student_id = self.student_combo.currentData()
        if not student_id:
            QMessageBox.warning(self, "Ошибка", "Выберите студента")
            return

        # Прогресс-диалог
        progress = QProgressDialog("Генерация зачётной книжки...", "Отмена", 0, 0, self)
        progress.setWindowTitle("Пожалуйста, подождите")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)
        progress.show()

        # Запуск в отдельном потоке
        self.thread = ReportGenerationThread('record_book', student_id=student_id)
        self.thread.finished.connect(lambda path: self.on_report_generated(path, progress))
        self.thread.error.connect(lambda error: self.on_report_error(error, progress))
        self.thread.start()

    def on_report_generated(self, file_path, progress):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "✅ Отчет сгенерирован",
            "Зачётная книжка успешно сгенерирована. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

        self.accept()

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{error}")


class GradesReportDialog(BaseReportDialog):
    """Диалог генерации ведомости успеваемости"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_groups()
        self.load_disciplines()

    def setup_ui(self):
        self.setWindowTitle("📊 Генерация ведомости успеваемости")
        self.setFixedSize(500, 300)

        # Главный layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Основной фрейм
        main_frame = self.create_main_frame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("Генерация ведомости успеваемости")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)

        # Группа формы
        form_group = QGroupBox("Параметры отчета")
        form_layout = QFormLayout()

        self.group_combo = QComboBox()
        self.discipline_combo = QComboBox()

        form_layout.addRow("👥 Группа:", self.group_combo)
        form_layout.addRow("📚 Дисциплина:", self.discipline_combo)

        form_group.setLayout(form_layout)
        frame_layout.addWidget(form_group)

        # Кнопки
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Сгенерировать")
        generate_btn.setObjectName("primary_button")
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_button")

        generate_btn.clicked.connect(self.generate_report)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(generate_btn)
        button_layout.addWidget(cancel_btn)

        frame_layout.addLayout(button_layout)

        main_frame.setLayout(frame_layout)
        layout.addWidget(main_frame)
        self.setLayout(layout)

    def load_groups(self):
        """Загрузка списка групп"""
        query = "SELECT id, name FROM groups ORDER BY name"
        result = db.execute_query(query)
        if result:
            self.group_combo.addItem("Выберите группу", None)
            for group_id, group_name in result:
                self.group_combo.addItem(group_name, group_id)

    def load_disciplines(self):
        """Загрузка списка дисциплин"""
        query = "SELECT id, name FROM disciplines ORDER BY name"
        result = db.execute_query(query)
        if result:
            self.discipline_combo.addItem("Выберите дисциплину", None)
            for disc_id, disc_name in result:
                self.discipline_combo.addItem(disc_name, disc_id)

    def generate_report(self):
        """Генерация отчета"""
        group_id = self.group_combo.currentData()
        discipline_id = self.discipline_combo.currentData()

        if not group_id or not discipline_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу и дисциплину")
            return

        progress = QProgressDialog("Генерация ведомости...", "Отмена", 0, 0, self)
        progress.setWindowTitle("Пожалуйста, подождите")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)
        progress.show()

        self.thread = ReportGenerationThread(
            'grades_report',
            group_id=group_id,
            discipline_id=discipline_id
        )
        self.thread.finished.connect(lambda path: self.on_report_generated(path, progress))
        self.thread.error.connect(lambda error: self.on_report_error(error, progress))
        self.thread.start()

    def on_report_generated(self, file_path, progress):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "✅ Отчет сгенерирован",
            "Ведомость успеваемости успешно сгенерирована. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

        self.accept()

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{error}")


class StudentRatingDialog(BaseReportDialog):
    """Диалог генерации рейтинга студентов"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_groups()

    def setup_ui(self):
        self.setWindowTitle("🏆 Генерация рейтинга студентов")
        self.setFixedSize(450, 250)

        # Главный layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Основной фрейм
        main_frame = self.create_main_frame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("Генерация рейтинга студентов")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)

        # Группа формы
        form_group = QGroupBox("Параметры отчета")
        form_layout = QFormLayout()

        self.group_combo = QComboBox()
        form_layout.addRow("👥 Группа:", self.group_combo)

        form_group.setLayout(form_layout)
        frame_layout.addWidget(form_group)

        # Кнопки
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Сгенерировать")
        generate_btn.setObjectName("primary_button")
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_button")

        generate_btn.clicked.connect(self.generate_report)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(generate_btn)
        button_layout.addWidget(cancel_btn)

        frame_layout.addLayout(button_layout)

        main_frame.setLayout(frame_layout)
        layout.addWidget(main_frame)
        self.setLayout(layout)

    def load_groups(self):
        """Загрузка списка групп"""
        query = "SELECT id, name FROM groups ORDER BY name"
        result = db.execute_query(query)
        if result:
            self.group_combo.addItem("Выберите группу", None)
            for group_id, group_name in result:
                self.group_combo.addItem(group_name, group_id)

    def generate_report(self):
        """Генерация отчета"""
        group_id = self.group_combo.currentData()
        if not group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу")
            return

        progress = QProgressDialog("Генерация рейтинга...", "Отмена", 0, 0, self)
        progress.setWindowTitle("Пожалуйста, подождите")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)
        progress.show()

        self.thread = ReportGenerationThread('student_rating', group_id=group_id)
        self.thread.finished.connect(lambda path: self.on_report_generated(path, progress))
        self.thread.error.connect(lambda error: self.on_report_error(error, progress))
        self.thread.start()

    def on_report_generated(self, file_path, progress):
        """Обработка успешной генерации отчета"""
        progress.close()

        reply = QMessageBox.question(
            self,
            "✅ Отчет сгенерирован",
            "Рейтинг студентов успешно сгенерирован. Хотите открыть файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.open_file(file_path)

        self.accept()

    def on_report_error(self, error, progress):
        """Обработка ошибки генерации"""
        progress.close()
        QMessageBox.critical(self, "❌ Ошибка", f"Не удалось сгенерировать отчет:\n{error}")