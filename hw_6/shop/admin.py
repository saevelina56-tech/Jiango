from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F, Count
from .models import Product, ProductImage, Order, OrderItem
from .admin_site import shop_admin_site

