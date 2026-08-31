from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    #avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
            verbose_name = 'тэг'
            verbose_name_plural = 'тэги'

class Category(models.Model):
    name = models.CharField(max_length=100, unique = True, verbose_name="название категории")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
        
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

    def __str__(self):
            return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    category = models.ForeignKey( 
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name="Категория"
    )
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False) 
    
    class Meta:
            ordering = ['-published_date']
            verbose_name = 'статья'
            verbose_name_plural = 'статьи'
      
        
        
class Genre(models.Model):
    """Модель жанра"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Модель книги"""
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Автор"
    )
    genres = models.ManyToManyField(
        Genre,
        related_name='books',
        verbose_name="Жанры"
    )
    publication_date = models.DateField(verbose_name="Дата публикации")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    pages = models.IntegerField(verbose_name="Количество страниц")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_available = models.BooleanField(default=True, verbose_name="Доступна")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-publication_date']

    def __str__(self):
        return self.title