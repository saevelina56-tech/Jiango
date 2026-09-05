from .base import BaseModel
from .product import Product, Category, ProductManager
from .order import Order, OrderItem
from django.db import models
from django.db.models import Sum, F, Count
from django.contrib.auth import get_user_model

class Category(BaseModel):
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
            ordering = ['last_name', 'first_name']
            verbose_name = 'Преподаватель'
            verbose_name_plural = 'Преподаватели'
            
    def __str__(self):
        return self.name
    
class ProductManager(BaseModel):
    def with_sales_annotation(self):
        return self.annotate(
            total_sales=Sum('order_items__quantity'),
            total_sales_count=Count('order_items')
        )
    
    def filter_by_price_range(self, min_price=None, max_price=None):
        queryset = self.all()
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        return queryset
    
    def get_most_sold(self, limit=10):
        return self.with_sales_annotation().order_by('-total_sales')[:limit]

class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name="Категория"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    objects = ProductManager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name'] 
    
    def __str__(self):
        return f'{self.name} - {self.price}'


User = get_user_model()

class Order(BaseModel):
    class StatusChoices(models.TextChoices):
        INPROCESS = 'inprocess', 'В процессе'
        FINISHED = 'finished', 'Завершенный'
        CANCELLED = 'cancelled', 'Отмененный'
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Пользователь"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices,
        default='pending',
        verbose_name="Статус"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Общая сумма"
    )
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'заказ №{self.id} - {self.user.email}'
    
    def calculate_total(self):
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
        self.total_amount = total
        self.save()
        return total