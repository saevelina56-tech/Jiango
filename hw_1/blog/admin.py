from django.contrib import admin
from .models import Tag, Article, Book, Author, Genre, Category

# Register your models here.
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Category)
