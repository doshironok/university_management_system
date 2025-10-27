from datetime import datetime
from database import db
from docxtpl import DocxTemplate
import os
import tempfile
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches


class ReportService:
    """Сервис для генерации отчетов"""

    @staticmethod
    def generate_student_record_book(student_id):
        """Генерация зачётной книжки для студента"""
        try:
            print(f"🔍 Поиск студента с ID: {student_id}")

            # Сначала проверим, существует ли студент
            check_query = "SELECT id, fio, record_book_id FROM students WHERE id = %s"
            check_result = db.execute_query(check_query, (student_id,))

            if not check_result:
                print(f"❌ Студент с ID {student_id} не найден в таблице students")
                raise Exception("Студент не найден")

            print(f"✅ Студент найден: {check_result[0]}")

            # Упрощенный запрос - только основные данные студента
            query = """
               SELECT s.fio, s.record_book_id, g.name as group_name
               FROM students s
               JOIN groups g ON s.group_id = g.id
               WHERE s.id = %s
               """
            student_data = db.execute_query(query, (student_id,))

            if not student_data:
                raise Exception("Данные студента не найдены")

            print(f"📊 Данные студента: {student_data[0]}")

            # Получаем оценки студента
            grades_query = """
               SELECT d.name as discipline_name, 
                      g.grade, 
                      g.type as control_type,
                      g.exam_date,
                      t.fio as teacher_name,
                      sp.semester
               FROM grades g
               JOIN study_plans sp ON g.study_plan_id = sp.id
               JOIN disciplines d ON sp.discipline_id = d.id
               LEFT JOIN teachers t ON sp.teacher_id = t.id
               WHERE g.student_id = %s
               ORDER BY sp.semester, d.name
               """
            grades_data = db.execute_query(grades_query, (student_id,))

            print(f"📚 Найдено оценок: {len(grades_data) if grades_data else 0}")

            # Группируем оценки по семестрам
            semesters = {}
            for grade in grades_data:
                semester = grade[5]
                if semester not in semesters:
                    semesters[semester] = []
                semesters[semester].append({
                    'discipline': grade[0],
                    'grade': grade[1],
                    'type': grade[2],
                    'date': grade[3].strftime('%d.%m.%Y') if grade[3] else '',
                    'teacher': grade[4] or ''
                })

            # Подготавливаем данные для шаблона
            context = {
                'student_fio': student_data[0][0],
                'record_book': student_data[0][1],
                'group': student_data[0][2],
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'semesters': []
            }

            for semester, grades in sorted(semesters.items()):
                context['semesters'].append({
                    'number': semester,
                    'grades': grades
                })

            return context

        except Exception as e:
            print(f"Ошибка при генерации зачётной книжки: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_grades_report(group_id, discipline_id):
        """Генерация ведомости успеваемости по группе и дисциплине"""
        # Используем функцию из БД
        grades_data = db.execute_query("SELECT * FROM generate_grades_report(%s, %s)", (group_id, discipline_id))

        # Получаем информацию о группе и дисциплине
        info_query = """
        SELECT g.name, d.name 
        FROM groups g, disciplines d 
        WHERE g.id = %s AND d.id = %s
        """
        info_data = db.execute_query(info_query, (group_id, discipline_id))

        if not info_data:
            return None

        context = {
            'group_name': info_data[0][0],
            'discipline_name': info_data[0][1],
            'current_date': datetime.now().strftime('%d.%m.%Y'),
            'grades': []
        }

        for grade in grades_data:
            context['grades'].append({
                'student_fio': grade[0],
                'grade': grade[1],
                'exam_date': grade[2].strftime('%d.%m.%Y') if grade[2] else 'Не сдано'
            })

        return context

    @staticmethod
    def generate_teacher_workload_report(teacher_id):
        """Генерация отчета по нагрузке преподавателя"""
        # Используем функцию из БД для общей нагрузки
        workload_data = db.execute_query("SELECT get_teacher_workload(%s)", (teacher_id,))

        # Детальная нагрузка
        detail_query = """
        SELECT d.name, g.name, sp.semester, sp.hours_lecture, sp.hours_practice,
               (sp.hours_lecture + sp.hours_practice) as total_hours
        FROM study_plans sp
        JOIN disciplines d ON sp.discipline_id = d.id
        JOIN groups g ON sp.group_id = g.id
        WHERE sp.teacher_id = %s
        ORDER BY g.name, sp.semester
        """
        detail_data = db.execute_query(detail_query, (teacher_id,))

        # Информация о преподавателе
        teacher_query = "SELECT fio, position FROM teachers WHERE id = %s"
        teacher_data = db.execute_query(teacher_query, (teacher_id,))

        if not teacher_data:
            return None

        context = {
            'teacher_fio': teacher_data[0][0],
            'teacher_position': teacher_data[0][1],
            'total_hours': workload_data[0][0] if workload_data else 0,
            'current_date': datetime.now().strftime('%d.%m.%Y'),
            'workload_details': []
        }

        for detail in detail_data:
            context['workload_details'].append({
                'discipline': detail[0],
                'group': detail[1],
                'semester': detail[2],
                'lecture_hours': detail[3],
                'practice_hours': detail[4],
                'total_hours': detail[5]
            })

        return context

    @staticmethod
    def generate_classroom_occupancy_report():
        """Генерация отчета по занятости аудиторий"""
        try:
            print("🔍 Генерация отчета по занятости аудиторий...")

            # Получаем данные о занятости аудиторий
            query = """
            SELECT 
                c.number as classroom_number,
                c.capacity,
                c.type as classroom_type,
                COUNT(s.id) as total_lessons,
                COUNT(DISTINCT s.discipline_id) as unique_disciplines,
                COUNT(DISTINCT s.teacher_id) as unique_teachers,
                STRING_AGG(DISTINCT TO_CHAR(s.start_time, 'Day'), ', ') as days_of_week
            FROM classrooms c
            LEFT JOIN schedule s ON c.id = s.classroom_id
            GROUP BY c.id, c.number, c.capacity, c.type
            ORDER BY c.number
            """

            print("📊 Выполняем запрос к БД...")
            classroom_data = db.execute_query(query)
            print(f"📋 Получено данных: {len(classroom_data) if classroom_data else 0} аудиторий")

            if not classroom_data:
                print("ℹ️ Нет данных об аудиториях")
                # Создаем тестовые данные для отладки
                classroom_data = [
                    ['101', 30, 'Лекционная', 10, 5, 3, 'Понедельник, Вторник'],
                    ['202', 20, 'Практическая', 8, 4, 2, 'Среда, Четверг']
                ]
                print("🛠️ Используем тестовые данные")

            # Подготавливаем данные для шаблона
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'classrooms': []
            }

            for classroom in classroom_data:
                context['classrooms'].append({
                    'number': str(classroom[0]) if classroom[0] else "Н/Д",
                    'capacity': str(classroom[1]) if classroom[1] else "0",
                    'type': str(classroom[2]) if classroom[2] else "Н/Д",
                    'total_lessons': str(classroom[3]) if classroom[3] else "0",
                    'unique_disciplines': str(classroom[4]) if classroom[4] else "0",
                    'unique_teachers': str(classroom[5]) if classroom[5] else "0",
                    'days_of_week': str(classroom[6]) if classroom[6] else "Нет занятий"
                })

            print(f"✅ Данные для отчета подготовлены: {len(context['classrooms'])} аудиторий")
            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации отчета по занятости аудиторий: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_student_rating_report(group_id):
        """Генерация рейтинга студентов группы"""
        try:
            print(f"🔍 Генерация рейтинга для группы ID: {group_id}")

            # Используем исправленную функцию из БД
            rating_data = db.execute_query("SELECT * FROM get_student_rating(%s)", (group_id,))

            if rating_data is None or rating_data is False:
                print("❌ Нет данных рейтинга или ошибка запроса")
                return None

            # Информация о группе
            group_query = "SELECT name FROM groups WHERE id = %s"
            group_data = db.execute_query(group_query, (group_id,))

            if not group_data:
                print("❌ Группа не найдена")
                return None

            context = {
                'group_name': group_data[0][0],
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'students': []
            }

            if rating_data:
                for student in rating_data:
                    context['students'].append({
                        'position': student[3] if len(student) > 3 else 0,  # student_rank
                        'fio': student[1] if len(student) > 1 else 'Неизвестно',
                        'avg_grade': float(student[2]) if student[2] and len(student) > 2 else 0.0
                    })
                print(f"✅ Найдено студентов в рейтинге: {len(rating_data)}")
            else:
                print("ℹ️ Нет данных для рейтинга")
                # Добавим тестовые данные для отладки
                context['students'] = [
                    {'position': 1, 'fio': 'Иванов Иван', 'avg_grade': 4.5},
                    {'position': 2, 'fio': 'Петров Петр', 'avg_grade': 4.2},
                    {'position': 3, 'fio': 'Сидорова Анна', 'avg_grade': 4.0}
                ]

            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации рейтинга студентов: {e}")
            import traceback
            traceback.print_exc()
            return None


class DocumentGenerator:
    """Класс для генерации документов из шаблонов"""

    @staticmethod
    def generate_document(template_name, context, output_filename):
        """Генерация документа из шаблона"""
        try:
            print(f"🔍 Начало генерации документа: {template_name}")

            # Путь к шаблонам
            templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
            template_path = os.path.join(templates_dir, template_name)

            print(f"🔍 Поиск шаблона: {template_path}")
            print(f"🔍 Директория шаблонов существует: {os.path.exists(templates_dir)}")

            if os.path.exists(templates_dir):
                files = os.listdir(templates_dir)
                print(f"📂 Файлы в директории templates: {files}")

            if not os.path.exists(template_path):
                error_msg = f"Шаблон {template_name} не найден по пути: {template_path}"
                print(f"❌ {error_msg}")
                raise FileNotFoundError(error_msg)

            print(f"✅ Шаблон найден, загружаем...")

            # Проверяем контекст
            print(f"📋 Контекст данных: {context.keys() if context else 'None'}")

            # Загружаем шаблон
            doc = DocxTemplate(template_path)
            print(f"✅ Шаблон загружен")

            # Заполняем шаблон данными
            print(f"🔍 Заполняем шаблон данными...")
            doc.render(context)
            print(f"✅ Шаблон заполнен")

            # Сохраняем документ
            project_root = os.path.join(os.path.dirname(__file__), '..')
            reports_dir = os.path.join(project_root, 'reports')

            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                print(f"✅ Создана папка reports: {reports_dir}")

            output_path = os.path.join(reports_dir, output_filename)
            print(f"💾 Сохраняем в: {output_path}")
            doc.save(output_path)

            print(f"✅ Документ сохранен: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Ошибка генерации документа: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_student_record_book(student_id):
        """Генерация зачётной книжки"""
        context = ReportService.generate_student_record_book(student_id)
        if not context:
            return None

        filename = f"record_book_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        return DocumentGenerator.generate_document('record_book_template.docx', context, filename)

    @staticmethod
    def generate_grades_report(group_id, discipline_id):
        """Генерация ведомости успеваемости"""
        context = ReportService.generate_grades_report(group_id, discipline_id)
        if not context:
            return None

        filename = f"grades_report_{group_id}_{discipline_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        return DocumentGenerator.generate_document('grades_report_template.docx', context, filename)

    @staticmethod
    def generate_teacher_workload_report(teacher_id):
        """Генерация отчета по нагрузке преподавателя"""
        try:
            print(f"🔍 Начало генерации отчета для teacher_id: {teacher_id}")

            context = ReportService.generate_teacher_workload_report(teacher_id)
            if not context:
                print("❌ Контекст не сгенерирован")
                return None

            print(f"✅ Контекст сгенерирован: {context.keys()}")

            filename = f"workload_report_{teacher_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            result = DocumentGenerator.generate_document('workload_report_template.docx', context, filename)

            if result:
                print(f"✅ Отчет успешно создан: {result}")
            else:
                print("❌ Не удалось создать отчет")

            return result

        except Exception as e:
            print(f"❌ Критическая ошибка в generate_teacher_workload_report: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_classroom_occupancy_report():
        """Генерация отчета по занятости аудиторий"""
        try:
            print("🔍 Начало генерации отчета по занятости аудиторий в DocumentGenerator")

            context = ReportService.generate_classroom_occupancy_report()
            if not context:
                print("❌ Контекст не сгенерирован")
                return None

            print(f"✅ Контекст сгенерирован: {len(context['classrooms'])} аудиторий")

            filename = f"classroom_occupancy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            result = DocumentGenerator.generate_document('classroom_occupancy_template.docx', context, filename)

            if result:
                print(f"✅ Отчет успешно создан: {result}")
            else:
                print("❌ Не удалось создать отчет")

            return result

        except Exception as e:
            print(f"❌ Критическая ошибка в generate_classroom_occupancy_report: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_student_rating_report(group_id):
        """Генерация рейтинга студентов"""
        try:
            context = ReportService.generate_student_rating_report(group_id)
            if not context:
                print("❌ Не удалось сгенерировать контекст для рейтинга")
                return None

            filename = f"student_rating_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            return DocumentGenerator.generate_document('student_rating_template.docx', context, filename)

        except Exception as e:
            print(f"❌ Ошибка в DocumentGenerator.generate_student_rating_report: {e}")
            return None
