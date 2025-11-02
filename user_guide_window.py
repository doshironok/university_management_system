# user_guide_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextBrowser, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont


class UserGuideWindow(QWidget):
    def __init__(self, user_role, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.setWindowTitle("📖 Инструкция пользователя")
        self.resize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#main_frame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel#title {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
            }
            QTextBrowser {
                background-color: #fafafa;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Основной фрейм
        main_frame = QFrame()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel("Инструкция пользователя")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)

        # Текст инструкции
        guide_text = self.get_guide_text()
        text_browser = QTextBrowser()
        text_browser.setHtml(guide_text)
        text_browser.setOpenExternalLinks(True)
        frame_layout.addWidget(text_browser)

        # Кнопка закрытия
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        frame_layout.addLayout(button_layout)

        main_frame.setLayout(frame_layout)
        layout.addWidget(main_frame)
        self.setLayout(layout)

    def get_guide_text(self):
        """Возвращает HTML-текст инструкции в зависимости от роли"""
        guides = {
            'teacher': self.get_teacher_guide(),
            'student': self.get_student_guide(),
            'kafedra': self.get_kafedra_guide(),
            'admin': self.get_admin_guide(),
            'dekanat': self.get_kafedra_guide(),  # dekanat = kafedra
        }
        return guides.get(self.user_role, self.get_default_guide())

    def get_teacher_guide(self):
        return """
        <h2>👨‍🏫 Инструкция для преподавателя</h2>
        <p><strong>Добро пожаловать в систему управления учебным процессом!</strong></p>

        <h3>Основные возможности:</h3>
        <ul>
            <li><strong>Мои дисциплины</strong> — просмотр списка дисциплин, которые вы ведёте.</li>
            <li><strong>Моё расписание</strong> — отображение ваших занятий по дням недели.</li>
            <li><strong>Успеваемость</strong> — выставление, редактирование и удаление оценок студентов.</li>
            <li><strong>Нагрузка</strong> — просмотр общей учебной нагрузки (лекции, практика, группы).</li>
            <li><strong>Отчёты</strong> — генерация официального отчёта по вашей нагрузке в формате DOCX.</li>
        </ul>

        <h3>Как выставить оценку:</h3>
        <ol>
            <li>Перейдите во вкладку <strong>«Успеваемость»</strong>.</li>
            <li>Выберите <strong>дисциплину</strong> и <strong>группу</strong> из выпадающих списков.</li>
            <li>Нажмите кнопку <strong>«Загрузить студентов»</strong>.</li>
            <li>В таблице найдите студента и дважды кликните по ячейке <strong>«Действия»</strong>.</li>
            <li>Выберите <strong>«Выставить оценку»</strong> или <strong>«Редактировать оценку»</strong>.</li>
            <li>Укажите оценку, тип контроля и дату, затем нажмите <strong>«Сохранить»</strong>.</li>
        </ol>

        <h3>Важно:</h3>
        <ul>
            <li>Вы можете выставлять оценки только по тем дисциплинам и группам, которые вам назначены.</li>
            <li>После выставления оценки она сразу отображается в зачётной книжке студента.</li>
            <li>Отчёт по нагрузке можно сохранить и распечатать для предоставления в деканат.</li>
        </ul>

        <p>При возникновении вопросов обратитесь к администратору системы.</p>
        """

    def get_student_guide(self):
        return """
        <h2>🎓 Инструкция для студента</h2>
        <p><strong>Добро пожаловать в личный кабинет студента!</strong></p>

        <h3>Основные возможности:</h3>
        <ul>
            <li><strong>Успеваемость</strong> — просмотр текущих оценок по всем дисциплинам.</li>
            <li><strong>Расписание</strong> — отображение ваших занятий по дням недели.</li>
            <li><strong>Зачётная книжка</strong> — полная история успеваемости по семестрам.</li>
            <li><strong>Отчёты</strong> — генерация официальной зачётной книжки в формате DOCX.</li>
        </ul>

        <h3>Как просмотреть успеваемость:</h3>
        <ol>
            <li>Перейдите во вкладку <strong>«Успеваемость»</strong>.</li>
            <li>В таблице отображаются все ваши оценки с указанием дисциплины, типа контроля и даты.</li>
            <li>Внизу показан ваш <strong>средний балл</strong> и количество сданных дисциплин.</li>
        </ol>

        <h3>Как получить зачётную книжку:</h3>
        <ol>
            <li>Перейдите во вкладку <strong>«Отчёты»</strong>.</li>
            <li>Нажмите кнопку <strong>«Зачётная книжка»</strong>.</li>
            <li>Система сгенерирует документ и предложит его открыть или сохранить.</li>
        </ol>

        <p>Все данные обновляются в реальном времени — как только преподаватель выставит оценку, она появится у вас.</p>
        """

    def get_kafedra_guide(self):
        return """
        <h2>🏢 Инструкция для сотрудника кафедры</h2>
        <p><strong>Вы управляете учебным процессом кафедры!</strong></p>

        <h3>Основные возможности:</h3>
        <ul>
            <li><strong>Дисциплины</strong> — добавление, редактирование и удаление дисциплин кафедры.</li>
            <li><strong>Преподаватели</strong> — управление составом кафедры.</li>
            <li><strong>Студенты</strong> — просмотр и редактирование данных студентов всех групп.</li>
            <li><strong>Учебные планы</strong> — формирование планов по дисциплинам и группам.</li>
            <li><strong>Расписание</strong> — составление и корректировка расписания занятий.</li>
            <li><strong>Отчёты</strong> — генерация ведомостей, рейтингов и отчётов по аудиториям.</li>
        </ul>

        <h3>Как добавить учебный план:</h3>
        <ol>
            <li>Перейдите во вкладку <strong>«Учебные планы»</strong>.</li>
            <li>Нажмите <strong>«Добавить учебный план»</strong>.</li>
            <li>Выберите дисциплину, группу, преподавателя, семестр и часы.</li>
            <li>Нажмите <strong>«Сохранить»</strong>.</li>
        </ol>

        <h3>Как сформировать ведомость:</h3>
        <ol>
            <li>Перейдите во вкладку <strong>«Отчёты»</strong>.</li>
            <li>Выберите <strong>«Ведомость успеваемости»</strong>.</li>
            <li>Укажите группу и дисциплину.</li>
            <li>Нажмите <strong>«Сгенерировать»</strong> — документ будет готов через несколько секунд.</li>
        </ol>

        <p>Вы видите только данные, относящиеся к вашей кафедре. Для управления всей системой используйте учётную запись администратора.</p>
        """

    def get_admin_guide(self):
        return """
        <h2>⚙️ Инструкция для администратора</h2>
        <p><strong>Вы управляете всей системой!</strong></p>

        <h3>Основные возможности:</h3>
        <ul>
            <li><strong>Пользователи</strong> — создание, редактирование и удаление всех учётных записей.</li>
            <li><strong>Кафедры</strong> — управление структурой кафедр университета.</li>
            <li><strong>Резервные копии</strong> — создание, восстановление и управление бэкапами БД.</li>
            <li><strong>Логи системы</strong> — просмотр истории изменений (если включено).</li>
            <li><strong>Оптимизация БД</strong> — выполнение команды <code>VACUUM ANALYZE</code> для повышения производительности.</li>
        </ul>

        <h3>Рекомендации:</h3>
        <ul>
            <li>Регулярно создавайте резервные копии (раз в день/неделю).</li>
            <li>Назначайте пользователям только необходимые роли.</li>
            <li>При удалении кафедры убедитесь, что на ней нет преподавателей.</li>
            <li>Используйте экспорт пользователей в CSV для аудита.</li>
        </ul>

        <p>Будьте осторожны: действия администратора необратимы!</p>
        """

    def get_default_guide(self):
        return "<p>Инструкция для вашей роли временно недоступна.</p>"