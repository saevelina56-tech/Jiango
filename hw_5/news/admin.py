from django.contrib import admin
from .models import Category, News

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content']