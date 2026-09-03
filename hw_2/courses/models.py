from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Instructor(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email', unique=True)
    specialization = models.CharField('Специализация', max_length=200)
    rating = models.DecimalField(
        'Рейтинг',
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0.0
    )
    start_date = models.DateField('Дата начала работы')
    biography = models.TextField('Биография', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.specialization})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    slug = models.SlugField('Slug', max_length=120, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name='Родительская категория'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
class Course(models.Model):
    class LevelChoices(models.TextChoices):
        BEGINNER = 'beginner', 'Начальный'
        INTERMEDIATE = 'intermediate', 'Средний'
        ADVANCED = 'advanced', 'Продвинутый'
    name = models.CharField('Название', unique=True)
    instructor = models.ForeignKey (
        Instructor,
        on_delete=models.SET_NULL,
        related_name='courses',
        verbose_name='Преподаватель'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Категория'
    )
    description = models.TextField('Описание', max_length=300)
    duration_hours = models.PositiveIntegerField('Длительность (часы)')
    level = models.CharField(
        'Сложность', 
        choices=LevelChoices.choices,
        default=LevelChoices.BEGINNER
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_published = models.BooleanField('Опубликован', default=False)
    max_students = models.PositiveIntegerField(
        'Количество мест',
        null=True,
        blank=True,
    )
    
    class Meta:
        ordering = ['-created_at', 'title']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    def available_spots(self):
        if self.max_students is None:
            return "Безлимитно"
        
        enrolled_count = self.enrollments.filter(
            status=Enrollment.StatusChoices.IN_PROGRESS
        ).count()
        
        free_spots = self.max_students - enrolled_count
        return max(0, free_spots)


class Student(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email', unique=True)
    registred_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    courses = models.ManyToManyField (
        Course,
        through='Enrollment',
        related_name='students',
        verbose_name='Курсы'
    )
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
        
class Enrollment(models.Model):
    class StatusChoices(models.TextChoices):
        INPROCESS = 'inprocess', 'В процессе'
        FINISHED = 'finished', 'Завершенный'
        CANCELLED = 'cancelled', 'Отмененный'
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,  
        related_name='enrollments',
        verbose_name='Студенты'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE, 
        related_name='enrollments',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField('Дата записи', auto_now_add=True)
    status = models.CharField(
        'Статус прохождения',
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.INPROCESS
    )
    progress = models.PositiveIntegerField(
        'Прогресс',
        validators=[MaxValueValidator(100)],
        default=0
    )
    grade = models.PositiveIntegerField(
        'Оценка',
        null=True,
        blank=True,
        validators=[MaxValueValidator(100)]
    )
    class Meta:
        ordering = ['-enrollment_date']
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student} → {self.course} ({self.get_status_display()})"
