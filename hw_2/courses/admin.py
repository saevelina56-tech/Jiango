from django.contrib import admin
from .models import Instructor, Category, Course, Student, Enrollment


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'specialization', 'rating', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    list_filter = ['parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ['student', 'status', 'progress', 'grade']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor', 'category', 'level', 'price', 'is_published']
    list_filter = ['level', 'is_published', 'category']
    search_fields = ['name', 'description']
    inlines = [EnrollmentInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'registration_at']
    search_fields = ['first_name', 'last_name', 'email']
    filter_horizontal = ['courses']  


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'process', 'grade', 'created_at']
    list_filter = ['status']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']