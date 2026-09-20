import os
import uuid
from django.db import models
from django.utils.text import slugify
from .utils import process_image


def product_image_path(instance, filename):
    ext = filename.split('.')[-1]
    name = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('products', str(instance.product_id), name)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_path)
    thumbnail = models.ImageField(upload_to=product_image_path, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.image and not self.pk:
            main_file, thumb_file = process_image(self.image)
            self.image.save(self.image.name, main_file, save=False)
            self.thumbnail.save(self.image.name, thumb_file, save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('done', 'Завершён'),
        ('canceled', 'Отменён'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity
    

    