from database import db
from datetime import datetime


class DataService:
    """Сервис для работы с данными с использованием существующих функций БД"""

    @staticmethod
    def get_all_students(group_id=None):
        """Получение списка студентов"""
        if group_id:
            query = """
            SELECT s.id, s.fio, s.record_book_id, g.name, s.status
            FROM students s
            JOIN groups g ON s.group_id = g.id
            WHERE s.group_id = %s
            ORDER BY s.fio
            """
            return db.execute_query(query, (group_id,))
        else:
            query = """
            SELECT s.id, s.fio, s.record_book_id, g.name, s.status
            FROM students s
            JOIN groups g ON s.group_id = g.id
            ORDER BY g.name, s.fio
            """
            return db.execute_query(query)

    @staticmethod
    def add_student(fio, record_book_id, group_id, status=True):
        """Добавление нового студента"""
        query = """
        INSERT INTO students (fio, record_book_id, group_id, status)
        VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (fio, record_book_id, group_id, status), fetch=False)

    @staticmethod
    def update_student(student_id, fio, record_book_id, group_id, status):
        """Обновление данных студента"""
        query = """
        UPDATE students 
        SET fio = %s, record_book_id = %s, group_id = %s, status = %s
        WHERE id = %s
        """
        return db.execute_query(query, (fio, record_book_id, group_id, status, student_id), fetch=False)

    @staticmethod
    def get_all_teachers():
        """Получение списка преподавателей"""
        query = """
        SELECT t.id, t.fio, t.position, t.academic_degree, d.name
        FROM teachers t
        JOIN departments d ON t.department_id = d.id
        ORDER BY t.fio
        """
        return db.execute_query(query)

    @staticmethod
    def add_teacher(fio, position, academic_degree, department_id):
        """Добавление нового преподавателя"""
        query = """
        INSERT INTO teachers (fio, position, academic_degree, department_id)
        VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (fio, position, academic_degree, department_id), fetch=False)

    @staticmethod
    def get_study_plans():
        """Получение учебных планов"""
        query = """
        SELECT sp.id, d.name, g.name, t.fio, sp.semester, 
               sp.hours_lecture, sp.hours_practice
        FROM study_plans sp
        JOIN disciplines d ON sp.discipline_id = d.id
        JOIN groups g ON sp.group_id = g.id
        LEFT JOIN teachers t ON sp.teacher_id = t.id
        ORDER BY g.name, sp.semester, d.name
        """
        return db.execute_query(query)

    @staticmethod
    def add_study_plan(discipline_id, group_id, teacher_id, semester, hours_lecture, hours_practice):
        """Добавление учебного плана"""
        query = """
        INSERT INTO study_plans (discipline_id, group_id, teacher_id, semester, hours_lecture, hours_practice)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (discipline_id, group_id, teacher_id, semester, hours_lecture, hours_practice),
                                fetch=False)

    # Использование существующих функций БД
    @staticmethod
    def add_grade(student_id, study_plan_id, grade, exam_date, grade_type):
        """Добавление оценки через хранимую процедуру"""
        query = "CALL add_grade(%s, %s, %s, %s, %s)"
        return db.execute_query(query, (student_id, study_plan_id, grade, exam_date, grade_type), fetch=False)

    @staticmethod
    def get_student_gpa(student_id):
        """Получение среднего балла студента через функцию БД"""
        query = "SELECT get_student_gpa(%s)"
        result = db.execute_query(query, (student_id,))
        return result[0][0] if result else 0

    @staticmethod
    def get_teacher_workload(teacher_id):
        """Получение нагрузки преподавателя через функцию БД"""
        query = "SELECT get_teacher_workload(%s)"
        result = db.execute_query(query, (teacher_id,))
        return result[0][0] if result else 0

    @staticmethod
    def generate_grades_report(group_id, discipline_id):
        """Генерация отчета по успеваемости через функцию БД"""
        query = "SELECT * FROM generate_grades_report(%s, %s)"
        return db.execute_query(query, (group_id, discipline_id))

    @staticmethod
    def backup_database():
        """Создание резервной копии через процедуру БД"""
        query = "CALL backup_database()"
        return db.execute_query(query, fetch=False)

    @staticmethod
    def add_schedule_entry(discipline_id, classroom_id, teacher_id, group_id, start_time, end_time, week_type):
        """Добавление занятия в расписание через процедуру БД"""
        query = "CALL add_schedule_entry(%s, %s, %s, %s, %s, %s, %s)"
        return db.execute_query(query,
                                (discipline_id, classroom_id, teacher_id, group_id, start_time, end_time, week_type),
                                fetch=False)

    @staticmethod
    def get_group_schedule(group_id):
        """Получение расписания группы через функцию БД"""
        query = "SELECT * FROM get_group_schedule(%s)"
        return db.execute_query(query, (group_id,))

    @staticmethod
    def get_teacher_schedule(teacher_id):
        """Получение расписания преподавателя через функцию БД"""
        query = "SELECT * FROM get_teacher_schedule(%s)"
        return db.execute_query(query, (teacher_id,))

    @staticmethod
    def check_classroom_availability(classroom_id, start_time, end_time, week_type):
        """Проверка доступности аудитории через функцию БД"""
        query = "SELECT check_classroom_availability(%s, %s, %s, %s)"
        result = db.execute_query(query, (classroom_id, start_time, end_time, week_type))
        return result[0][0] if result else False

    @staticmethod
    def generate_classroom_occupancy_report():
        """Генерация отчета по занятости аудиторий через функцию БД"""
        query = "SELECT * FROM generate_classroom_occupancy_report()"
        return db.execute_query(query)

    @staticmethod
    def get_student_rating(group_id):
        """Получение академического рейтинга студентов через функцию БД"""
        query = "SELECT * FROM get_student_rating(%s)"
        return db.execute_query(query, (group_id,))

    @staticmethod
    def get_student_grades(student_id):
        """Получение оценок студента"""
        query = """
        SELECT g.id, d.name, g.grade, g.type, g.exam_date, t.fio, sp.semester
        FROM grades g
        JOIN study_plans sp ON g.study_plan_id = sp.id
        JOIN disciplines d ON sp.discipline_id = d.id
        LEFT JOIN teachers t ON sp.teacher_id = t.id
        WHERE g.student_id = %s
        ORDER BY g.exam_date DESC
        """
        return db.execute_query(query, (student_id,))

    @staticmethod
    def get_teacher_disciplines(teacher_id):
        """Получение дисциплин преподавателя"""
        query = """
        SELECT DISTINCT d.id, d.name
        FROM study_plans sp
        JOIN disciplines d ON sp.discipline_id = d.id
        WHERE sp.teacher_id = %s
        ORDER BY d.name
        """
        return db.execute_query(query, (teacher_id,))

    @staticmethod
    def get_groups_for_discipline(discipline_id, teacher_id):
        """Получение групп для дисциплины преподавателя"""
        query = """
        SELECT DISTINCT g.id, g.name
        FROM study_plans sp
        JOIN groups g ON sp.group_id = g.id
        WHERE sp.discipline_id = %s AND sp.teacher_id = %s
        ORDER BY g.name
        """
        return db.execute_query(query, (discipline_id, teacher_id))

    @staticmethod
    def get_students_for_grading(group_id, discipline_id, teacher_id):
        """Получение студентов для выставления оценок"""
        query = """
        SELECT s.id, s.fio, s.record_book_id,
               COALESCE(g.grade, 'Нет оценки'),
               COALESCE(g.id, NULL),
               sp.id as study_plan_id
        FROM students s
        JOIN study_plans sp ON s.group_id = sp.group_id
        LEFT JOIN grades g ON g.student_id = s.id AND g.study_plan_id = sp.id
        WHERE s.group_id = %s 
          AND sp.discipline_id = %s 
          AND sp.teacher_id = %s
          AND s.status = true
        ORDER BY s.fio
        """
        return db.execute_query(query, (group_id, discipline_id, teacher_id))

    @staticmethod
    def update_grade(grade_id, grade, exam_date, grade_type):
        """Обновление оценки"""
        query = """
        UPDATE grades 
        SET grade = %s, exam_date = %s, type = %s
        WHERE id = %s
        """
        return db.execute_query(query, (grade, exam_date, grade_type, grade_id), fetch=False)

    @staticmethod
    def get_detailed_workload(teacher_id):
        """Детальная нагрузка преподавателя"""
        query = """
        SELECT d.name, g.name, sp.hours_lecture, sp.hours_practice,
               (sp.hours_lecture + sp.hours_practice), sp.semester
        FROM study_plans sp
        JOIN disciplines d ON sp.discipline_id = d.id
        JOIN groups g ON sp.group_id = g.id
        WHERE sp.teacher_id = %s
        ORDER BY g.name, sp.semester, d.name
        """
        return db.execute_query(query, (teacher_id,))