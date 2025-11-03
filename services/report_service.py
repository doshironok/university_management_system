from datetime import datetime
from database import db
from docxtpl import DocxTemplate, InlineImage
import os
import tempfile
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from docx.shared import Mm

class ReportService:
    """Сервис для генерации отчетов"""

    @staticmethod
    def generate_student_record_book(student_id):
        """Генерация зачётной книжки для студента по обновлённому шаблону"""
        try:
            print(f"🔍 Поиск студента с ID: {student_id}")

            # 1. Основные данные студента + группа + направление + факультет + год поступления
            student_query = """
            SELECT 
                s.fio, 
                s.record_book_id,
                g.name as group_name,
                g.creation_year as enrollment_year,
                sp.code as program_code,
                sp.name as program_name,
                'Факультет ИТиК' as faculty  --фиксированное значение, так как в БД нет таблицы faculties
            FROM students s
            JOIN groups g ON s.group_id = g.id
            JOIN study_programs sp ON g.study_program_id = sp.id
            WHERE s.id = %s
            """
            student_data = db.execute_query(student_query, (student_id,))
            if not student_data:
                raise Exception("Студент не найден")

            student_row = student_data[0]
            student_fio = student_row[0]
            record_book = student_row[1]
            group = student_row[2]
            enrollment_year = student_row[3]
            program = f"{student_row[4]} – {student_row[5]}"  # Код + название
            faculty = student_row[6]

            # 2. Все оценки с деталями
            grades_query = """
            SELECT 
                d.name as discipline_name,
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
            if not grades_data:
                grades_data = []

            # 3. Группировка по семестрам с расчётом среднего балла и статистики
            semesters = {}
            all_numeric_grades = []
            total_disciplines = 0
            total_passed = 0  # Считаем "зачёт", "3+", "4", "5" как сданное

            for grade in grades_data:
                discipline = grade[0]
                grade_val = grade[1]
                grade_type = grade[2]
                exam_date = grade[3]
                teacher = grade[4] or ''
                semester_num = grade[5]

                # Инициализация семестра
                if semester_num not in semesters:
                    semesters[semester_num] = {
                        'number': semester_num,
                        'grades': [],
                        'numeric_grades': [],
                        'passed_count': 0,
                        'total_count': 0
                    }

                # Преобразуем дату в строку
                date_str = exam_date.strftime('%d.%m.%Y') if exam_date else ''

                # Добавляем оценку в список
                semesters[semester_num]['grades'].append({
                    'discipline': discipline,
                    'type': grade_type,
                    'grade': grade_val,
                    'date': date_str,
                    'teacher': teacher
                })

                # Обновляем статистику по семестру
                semesters[semester_num]['total_count'] += 1
                total_disciplines += 1

                # Обработка "зачёт/незачёт"
                if grade_val == 'зачёт':
                    semesters[semester_num]['passed_count'] += 1
                    total_passed += 1
                    # Не добавляем в числовой балл
                elif grade_val == 'незачёт':
                    # Не сдано — ничего не добавляем
                    pass
                # Числовые оценки
                elif grade_val and grade_val.isdigit():
                    numeric_grade = int(grade_val)
                    semesters[semester_num]['numeric_grades'].append(numeric_grade)
                    all_numeric_grades.append(numeric_grade)
                    if numeric_grade >= 3:
                        semesters[semester_num]['passed_count'] += 1
                        total_passed += 1
                # Другие оценки (например, "неявка") — игнорируем

            # 4. Вычисляем средние баллы по семестрам
            for semester in semesters.values():
                grades_list = semester['numeric_grades']
                avg = sum(grades_list) / len(grades_list) if grades_list else 0.0
                semester['avg_grade'] = f"{avg:.2f}"
                # Также сохраняем статистику для отчёта (опционально)
                semester['passed'] = semester['passed_count']
                semester['total'] = semester['total_count']

            # 5. Общий средний балл (только числовые оценки)
            overall_avg = sum(all_numeric_grades) / len(all_numeric_grades) if all_numeric_grades else 0.0

            # 6. Общее количество часов (без изменений)
            hours_query = """
            SELECT COALESCE(SUM(sp.hours_lecture + sp.hours_practice), 0)
            FROM study_plans sp
            JOIN students s ON sp.group_id = s.group_id
            WHERE s.id = %s
            """
            hours_result = db.execute_query(hours_query, (student_id,))
            total_hours = hours_result[0][0] if hours_result else 0

            # 7. Формируем контекст
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'record_book': record_book,
                'student_fio': student_fio,
                'group': group,
                'program': program,
                'faculty': faculty,
                'enrollment_year': enrollment_year,
                'semesters': [],
                'overall_avg_grade': f"{overall_avg:.2f}",
                'total_disciplines': total_disciplines,
                'total_passed': total_passed,  # ← Добавлено: количество сданных
                'total_hours': total_hours
            }

            # Сортируем семестры по номеру
            for semester_num in sorted(semesters.keys()):
                context['semesters'].append(semesters[semester_num])

            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации зачётной книжки: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_grades_report(group_id, discipline_id):
        """Генерация ведомости успеваемости с диаграммой и статистикой"""
        try:
            print(f"🔍 Генерация ведомости для группы {group_id}, дисциплины {discipline_id}")

            # 1. Основная информация
            info_query = """
            SELECT g.name, d.name, t.fio, sp.semester,
                   (sp.hours_lecture + sp.hours_practice)
            FROM study_plans sp
            JOIN groups g ON sp.group_id = g.id
            JOIN disciplines d ON sp.discipline_id = d.id
            LEFT JOIN teachers t ON sp.teacher_id = t.id
            WHERE sp.group_id = %s AND sp.discipline_id = %s
            LIMIT 1
            """
            info_data = db.execute_query(info_query, (group_id, discipline_id))
            if not info_data:
                raise Exception("Учебный план не найден")
            row = info_data[0]
            group_name = row[0]
            discipline_name = row[1]
            teacher_name = row[2] or 'Не назначен'
            semester = row[3]
            total_hours = row[4] or 0

            # 2. Все студенты группы
            students_query = """
            SELECT s.id, s.fio, s.record_book_id, s.status
            FROM students s
            WHERE s.group_id = %s
            ORDER BY s.fio
            """
            students_data = db.execute_query(students_query, (group_id,))
            if not students_data:
                students_data = []

            # 3. Оценки по дисциплине
            grades_query = """
            SELECT g.student_id, g.grade, g.exam_date, g.type
            FROM grades g
            JOIN study_plans sp ON g.study_plan_id = sp.id
            WHERE sp.group_id = %s AND sp.discipline_id = %s
            """
            grades_data = db.execute_query(grades_query, (group_id, discipline_id))
            grades_dict = {}
            if grades_data:
                for grade_row in grades_data:
                    student_id = grade_row[0]
                    grades_dict[student_id] = {
                        'grade': grade_row[1],
                        'exam_date': grade_row[2],
                        'control_type': grade_row[3]
                    }

            # 4. Формируем список студентов с оценками
            grades = []
            passed = failed = 0
            all_numeric_grades = []

            for i, student in enumerate(students_data, 1):
                student_id, fio, record_book, status = student
                grade_info = grades_dict.get(student_id)

                if grade_info:
                    grade_val = grade_info['grade']
                    exam_date = grade_info['exam_date']
                    control_type = grade_info['control_type']
                    date_str = exam_date.strftime('%d.%m.%Y') if exam_date else ''
                else:
                    grade_val = 'Нет оценки'
                    date_str = ''
                    control_type = ''

                grades.append({
                    'position': i,
                    'student_fio': fio,
                    'grade': grade_val,
                    'exam_date': date_str,
                    'control_type': control_type,
                    'record_book': record_book
                })

                # Статистика
                if grade_val == 'зачёт':
                    passed += 1
                elif grade_val == 'незачёт':
                    failed += 1
                elif grade_val and grade_val.isdigit():
                    numeric_grade = int(grade_val)
                    all_numeric_grades.append(numeric_grade)
                    if numeric_grade >= 3:
                        passed += 1
                    else:
                        failed += 1

            total_students = len(grades)
            avg_grade = sum(all_numeric_grades) / len(all_numeric_grades) if all_numeric_grades else 0.0

            # 5. Создаём круговую диаграмму
            pie_chart = None
            if total_students > 0:
                from docxtpl import InlineImage
                import matplotlib.pyplot as plt
                import io
                from docx.shared import Mm

                labels = []
                sizes = []
                colors = []
                if passed > 0:
                    labels.append('Сдали')
                    sizes.append(passed)
                    colors.append('#27ae60')  # Зелёный
                if failed > 0:
                    labels.append('Не сдали')
                    sizes.append(failed)
                    colors.append('#e74c3c')  # Красный

                if labels:
                    plt.figure(figsize=(6, 6))
                    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                    plt.title('Результаты по дисциплине', fontsize=14)
                    plt.axis('equal')

                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight')
                    img_buffer.seek(0)
                    plt.close()
                    pie_chart = img_buffer  # Передаём буфер, а не InlineImage

            # 6. Формируем контекст
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'group_name': group_name,
                'discipline_name': discipline_name,
                'teacher_name': teacher_name,
                'semester': semester,
                'total_hours': total_hours,
                'grades': grades,
                'total_students': total_students,
                'passed_count': passed,
                'failed_count': failed,
                'avg_grade': f"{avg_grade:.2f}",
                'pie_chart': pie_chart
            }

            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации ведомости: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_teacher_workload_report(teacher_id):
        """Генерация отчёта по нагрузке преподавателя с диаграммой"""
        try:
            print(f"🔍 Генерация отчёта по нагрузке для teacher_id: {teacher_id}")

            # 1. Основные данные преподавателя
            teacher_query = """
            SELECT t.fio, t.position, d.name as department_name
            FROM teachers t
            JOIN departments d ON t.department_id = d.id
            WHERE t.id = %s
            """
            teacher_result = db.execute_query(teacher_query, (teacher_id,))
            if not teacher_result:
                raise Exception("Преподаватель не найден")
            teacher_fio, teacher_position, department_name = teacher_result[0]

            # 2. Общая статистика
            total_query = """
            SELECT 
                COALESCE(SUM(hours_lecture + hours_practice), 0),
                COALESCE(SUM(hours_lecture), 0),
                COALESCE(SUM(hours_practice), 0)
            FROM study_plans
            WHERE teacher_id = %s
            """
            total_result = db.execute_query(total_query, (teacher_id,))
            total_hours, lecture_hours, practice_hours = total_result[0] if total_result else (0, 0, 0)

            # 3. Детализация
            detail_query = """
            SELECT d.name, g.name, sp.semester, sp.hours_lecture, sp.hours_practice,
                   (sp.hours_lecture + sp.hours_practice) as total_hours
            FROM study_plans sp
            JOIN disciplines d ON sp.discipline_id = d.id
            JOIN groups g ON sp.group_id = g.id
            WHERE sp.teacher_id = %s
            ORDER BY g.name, d.name
            """
            detail_result = db.execute_query(detail_query, (teacher_id,))
            workload_details = []
            disciplines = []
            lecture_data = []
            practice_data = []

            for row in detail_result:
                detail = {
                    'discipline': row[0],
                    'group': row[1],
                    'semester': row[2],
                    'lecture_hours': row[3],
                    'practice_hours': row[4],
                    'total_hours': row[5]
                }
                workload_details.append(detail)
                disciplines.append(f"{row[0]}\n({row[1]})")
                lecture_data.append(row[3])
                practice_data.append(row[4])

            # 4. Создаём столбчатую диаграмму
            bar_chart = None
            if disciplines:
                import matplotlib.pyplot as plt
                import io
                from docx.shared import Mm
                from docxtpl import InlineImage

                plt.figure(figsize=(10, 6))
                x = range(len(disciplines))
                plt.bar(x, lecture_data, label='Лекции', color='#3498db')
                plt.bar(x, practice_data, bottom=lecture_data, label='Практика', color='#2ecc71')
                plt.xlabel('Дисциплины (Группы)')
                plt.ylabel('Часы')
                plt.title('Распределение учебной нагрузки', fontsize=14)
                plt.xticks(x, disciplines, rotation=45, ha='right')
                plt.legend()
                plt.tight_layout()

                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                plt.close()
                bar_chart = img_buffer  # Передаём буфер

            # 5. Формируем контекст
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'teacher_fio': teacher_fio,
                'teacher_position': teacher_position,
                'department_name': department_name,
                'total_hours': total_hours,
                'lecture_hours': lecture_hours,
                'practice_hours': practice_hours,
                'workload_details': workload_details,
                'bar_chart': bar_chart
            }

            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации отчёта по нагрузке: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_classroom_occupancy_report(building_filter=None):
        """Генерация отчёта по занятости аудиторий с поддержкой фильтрации и статистики"""
        try:
            print("🔍 Генерация отчёта по занятости аудиторий...")

            # 1. Формируем фильтр по корпусу
            building_where = ""
            building_params = []
            if building_filter:
                building_where = "AND c.building = %s"
                building_params = [building_filter]

            # 2. Запрос для расчёта занятости
            query = f"""
            SELECT 
                c.number,
                c.building,
                c.capacity,
                c.type,
                COUNT(s.id) as total_lessons
            FROM classrooms c
            LEFT JOIN schedule s ON c.id = s.classroom_id
            WHERE 1=1 {building_where}
            GROUP BY c.id, c.number, c.building, c.capacity, c.type
            ORDER BY c.building, c.number
            """
            params = building_params
            classroom_data = db.execute_query(query, params)
            if not classroom_data:
                classroom_data = []

            # 3. Подготавливаем данные с расчётом загруженности
            classrooms = []
            total_lessons_all = 0
            occupancy_rates = []

            for row in classroom_data:
                number = str(row[0])
                building = str(row[1]) if row[1] else "Н/Д"
                capacity = int(row[2]) if row[2] else 0
                room_type = str(row[3]) if row[3] else "Н/Д"
                total_lessons = int(row[4]) if row[4] else 0

                # Расчёт загруженности: максимум 84 пары в неделю (6 дней × 14 пар)
                max_lessons_per_week = 84
                occupancy_rate = (total_lessons / max_lessons_per_week * 100) if max_lessons_per_week > 0 else 0.0

                classrooms.append({
                    'number': number,
                    'building': building,
                    'capacity': capacity,
                    'type': room_type,
                    'total_lessons': total_lessons,
                    'occupancy_rate': f"{occupancy_rate:.1f}%"
                })

                total_lessons_all += total_lessons
                occupancy_rates.append(occupancy_rate)

            # 4. Сводная статистика
            total_classrooms = len(classrooms)
            avg_occupancy = sum(occupancy_rates) / len(occupancy_rates) if occupancy_rates else 0.0

            summary = {
                'total_classrooms': total_classrooms,
                'total_lessons': total_lessons_all,
                'avg_occupancy_rate': f"{avg_occupancy:.1f}%"
            }

            # 5. Формируем контекст
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'building_filter': f"Корпус: {building_filter}" if building_filter else "Все корпуса",
                'classrooms': classrooms,
                'summary': summary
            }

            return context

        except Exception as e:
            print(f"❌ Ошибка при генерации отчёта по занятости аудиторий: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def generate_student_rating_report(group_id):
        """Генерация академического рейтинга студентов с расширенной статистикой и диаграммой"""
        try:
            print(f"🔍 Генерация рейтинга для группы ID: {group_id}")

            # 1. Получаем данные группы
            group_query = """
            SELECT name, creation_year
            FROM groups
            WHERE id = %s
            """
            group_result = db.execute_query(group_query, (group_id,))
            if not group_result:
                raise Exception("Группа не найдена")
            group_name = group_result[0][0]
            creation_year = group_result[0][1]
            course = 2025 - creation_year + 1
            semester = (course - 1) * 2 + 1

            # 2. Получаем рейтинг через функцию БД
            rating_data = db.execute_query("SELECT * FROM get_student_rating(%s)", (group_id,))
            if not rating_data:
                rating_data = []

            # 3. Классифицируем студентов
            students = []
            excellent = good = satisfactory = debt = 0
            excellent_list = []
            good_list = []
            satisfactory_list = []
            debt_list = []

            for record in rating_data:
                position = record[3]
                fio = record[1]
                avg_grade = float(record[2]) if record[2] else 0.0

                student = {
                    'position': position,
                    'fio': fio,
                    'avg_grade': avg_grade
                }
                students.append(student)

                if avg_grade >= 4.5:
                    excellent += 1
                    excellent_list.append(fio)
                elif avg_grade >= 3.5:
                    good += 1
                    good_list.append(fio)
                elif avg_grade >= 2.5:
                    satisfactory += 1
                    satisfactory_list.append(fio)
                else:
                    debt += 1
                    debt_list.append(fio)

            total = len(students)
            excellent_pct = (excellent / total * 100) if total > 0 else 0.0
            good_pct = (good / total * 100) if total > 0 else 0.0
            satisfactory_pct = (satisfactory / total * 100) if total > 0 else 0.0
            debt_pct = (debt / total * 100) if total > 0 else 0.0

            group_avg_grade = sum(s['avg_grade'] for s in students) / total if total > 0 else 0.0
            best_student = max(students, key=lambda x: x['avg_grade']) if students else None

            # 4. Создаём круговую диаграмму
            from docxtpl import InlineImage
            import matplotlib.pyplot as plt
            import io
            from docx.shared import Mm

            pie_chart = None
            if total > 0:
                labels = []
                sizes = []
                colors = []
                if excellent > 0:
                    labels.append('Отличники (≥4.5)')
                    sizes.append(excellent_pct)
                    colors.append('#27ae60')  # Зелёный
                if good > 0:
                    labels.append('Хорошисты (3.5–4.4)')
                    sizes.append(good_pct)
                    colors.append('#2ecc71')  # Светло-зелёный
                if satisfactory > 0:
                    labels.append('Троечники (2.5–3.4)')
                    sizes.append(satisfactory_pct)
                    colors.append('#f39c12')  # Оранжевый
                if debt > 0:
                    labels.append('Должники (<2.5)')
                    sizes.append(debt_pct)
                    colors.append('#e74c3c')  # Красный

                if labels:
                    plt.figure(figsize=(6, 6))
                    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                    plt.title('Академическая успеваемость группы', fontsize=14)
                    plt.axis('equal')

                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight')
                    img_buffer.seek(0)
                    plt.close()
                    pie_chart = img_buffer

            # 5. Формируем контекст
            context = {
                'current_date': datetime.now().strftime('%d.%m.%Y'),
                'group_name': group_name,
                'course': course,
                'semester': semester,
                'total_students': total,
                'students': students,
                'group_avg_grade': f"{group_avg_grade:.2f}",
                'best_student': best_student['fio'] if best_student else "Нет данных",
                'best_grade': f"{best_student['avg_grade']:.2f}" if best_student else "0.00",

                # Новые поля для категорий
                'excellent_count': excellent,
                'excellent_pct': f"{excellent_pct:.1f}",
                'good_count': good,
                'good_pct': f"{good_pct:.1f}",
                'satisfactory_count': satisfactory,
                'satisfactory_pct': f"{satisfactory_pct:.1f}",
                'debt_count': debt,
                'debt_pct': f"{debt_pct:.1f}",

                # Диаграмма
                'pie_chart': pie_chart
            }

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
        try:
            templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
            template_path = os.path.join(templates_dir, template_name)
            doc = DocxTemplate(template_path)

            # Создаём InlineImage для диаграмм (если есть)
            if 'bar_chart' in context and context['bar_chart']:
                context['bar_chart'] = InlineImage(doc, context['bar_chart'], width=Mm(160))
            if 'pie_chart' in context and context['pie_chart']:
                context['pie_chart'] = InlineImage(doc, context['pie_chart'], width=Mm(100))

            doc.render(context)
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, output_filename)
            doc.save(output_path)
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
