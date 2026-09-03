from django.db.models import Count, Avg, Q, F, Value, IntegerField
from django.db.models.functions import Coalesce
from django.db import transaction
from .models import Course, Instructor, Student, Enrollment, Category

def get_published_courses():
    return Course.objects.filter(
        is_published=True
    ).select_related(
        'instructor', 
        'category'
    ).order_by('-created_at')


def get_courses_by_level(level):
    return Course.objects.filter(
        level=level
    ).select_related(
        'instructor', 
        'category'
    ).order_by('title')


def get_instructor_courses(instructor_id):
    return Course.objects.filter(
        instructor_id=instructor_id
    ).select_related(
        'category'
    ).order_by('-created_at')


def get_popular_courses(min_students):
    return Course.objects.filter(
        is_published=True
    ).annotate(
        student_count=Count('students', distinct=True)
    ).filter(
        student_count__gte=min_students
    ).select_related(
        'instructor', 
        'category'
    ).order_by('-student_count')


def get_student_active_courses(student_id):
    return Course.objects.filter(
        enrollments__student_id=student_id,
        enrollments__status=Enrollment.StatusChoices.IN_PROGRESS
    ).select_related(
        'instructor', 
        'category'
    ).order_by('-created_at')


def get_category_with_subcategories(category_id):
    def get_all_subcategories(category):
        """Рекурсивно собирает все подкатегории"""
        subcategories = list(category.subcategories.all())
        result = subcategories.copy()
        for subcat in subcategories:
            result.extend(get_all_subcategories(subcat))
        return result
    
    try:
        category = Category.objects.get(id=category_id)
        return {
            'category': category,
            'subcategories': get_all_subcategories(category)
        }
    except Category.DoesNotExist:
        return None


def get_expensive_courses(min_price):
    return Course.objects.filter(
        price__gt=min_price,
        is_published=True
    ).select_related(
        'instructor', 
        'category'
    ).order_by('-price')


def get_instructors_by_rating(min_rating):
    return Instructor.objects.filter(
        rating__gte=min_rating,
        is_active=True
    ).order_by('-rating', 'last_name', 'first_name')


def get_courses_with_available_spots():
    limited_courses = Course.objects.filter(
        is_published=True,
        max_students__isnull=False
    ).annotate(
        enrolled_count=Count(
            'enrollments',
            filter=Q(enrollments__status=Enrollment.StatusChoices.IN_PROGRESS)
        )
    ).filter(
        enrolled_count__lt=F('max_students')
    )
    
    unlimited_courses = Course.objects.filter(
        is_published=True,
        max_students__isnull=True
    )
    
    return (limited_courses | unlimited_courses).select_related(
        'instructor', 
        'category'
    ).order_by('title')


def update_enrollment_progress(enrollment_id, progress):
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        
        if not (0 <= progress <= 100):
            raise ValueError("Прогресс должен быть от 0 до 100")
        
        enrollment.progress = progress
        
        if progress == 100 and enrollment.status != Enrollment.StatusChoices.COMPLETED:
            enrollment.status = Enrollment.StatusChoices.COMPLETED
        
        enrollment.save()
        return enrollment
    
    except Enrollment.DoesNotExist:
        return None
    except ValueError as e:
        raise e


@transaction.atomic
def complete_enrollment(enrollment_id, grade):
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        
        if not (0 <= grade <= 100):
            raise ValueError("Оценка должна быть от 0 до 100")
        
        enrollment.status = Enrollment.StatusChoices.COMPLETED
        enrollment.progress = 100
        enrollment.grade = grade
        enrollment.save()
        
        return enrollment
    
    except Enrollment.DoesNotExist:
        return None
    except ValueError as e:
        raise e


def get_student_statistics(student_id):
    try:
        student = Student.objects.prefetch_related(
            'enrollments'
        ).get(id=student_id)
        
        enrollments = student.enrollments.all()
        
        total_courses = enrollments.count()
        
        completed_enrollments = enrollments.filter(
            status=Enrollment.StatusChoices.COMPLETED
        )
        completed_courses = completed_enrollments.count()
        
        completed_with_grade = completed_enrollments.filter(
            grade__isnull=False
        )
        
        if completed_with_grade.exists():
            avg_grade = completed_with_grade.aggregate(
                avg=Avg('grade')
            )['avg']
            avg_grade = round(avg_grade, 2) if avg_grade else None
        else:
            avg_grade = None
        
        in_progress = enrollments.filter(
            status=Enrollment.StatusChoices.IN_PROGRESS
        ).count()
        
        cancelled = enrollments.filter(
            status=Enrollment.StatusChoices.CANCELLED
        ).count()
        
        total_progress = enrollments.aggregate(
            total=Coalesce(Avg('progress'), Value(0))
        )['total']
        
        return {
            'student': student,
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'average_grade': avg_grade,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'total_progress': round(total_progress, 1) if total_progress else 0,
        }
    
    except Student.DoesNotExist:
        return None


def get_instructor_statistics(instructor_id):
    try:
        instructor = Instructor.objects.prefetch_related(
            'courses',
            'courses__reviews'
        ).get(id=instructor_id)
        
        courses = instructor.courses.all()
        total_courses = courses.count()
        
        students_count = Student.objects.filter(
            enrollments__course__in=courses
        ).distinct().count()
        
        published_courses = courses.filter(is_published=True).count()
        
        avg_course_rating = None
        all_reviews = []
        for course in courses:
            all_reviews.extend(course.reviews.all())
        
        if all_reviews:
            avg_course_rating = round(
                sum(r.rating for r in all_reviews) / len(all_reviews), 
                1
            )
        
        courses_stats = courses.annotate(
            student_count=Count('students', distinct=True)
        ).values('title', 'student_count', 'is_published')
        
        total_enrollments = Enrollment.objects.filter(
            course__in=courses
        ).count()
        
        completed_enrollments = Enrollment.objects.filter(
            course__in=courses,
            status=Enrollment.StatusChoices.COMPLETED
        ).count()
        
        return {
            'instructor': instructor,
            'total_courses': total_courses,
            'published_courses': published_courses,
            'total_students': students_count,
            'average_course_rating': avg_course_rating,
            'total_enrollments': total_enrollments,
            'completed_enrollments': completed_enrollments,
            'courses_stats': list(courses_stats),
            'completion_rate': round(
                (completed_enrollments / total_enrollments * 100) 
                if total_enrollments > 0 else 0, 
                1
            ),
        }
    
    except Instructor.DoesNotExist:
        return None

