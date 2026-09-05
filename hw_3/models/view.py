from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.views.generic import TemplateView
from django.db import connection
from ..models import Category, Product, Order, OrderItem

class AnalyticsView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        categories = self._get_categories_with_analytics()
        
        top_products = self._get_top_products_raw_sql()
        
        context.update({
            'categories': categories,
            'top_products': top_products,
            'total_categories': categories.count(),
            'total_products': Product.objects.count(),
            'total_orders': Order.objects.count(),
        })
        
        return context

    def _get_categories_with_analytics(self):
        categories = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True)),
            total_sales=Sum('products__order_items__quantity'),
            total_revenue=Sum(F('products__order_items__quantity') * F('products__order_items__price'))
        ).order_by('-total_sales')
        
        categories = categories.prefetch_related(
            'products',
            'products__order_items',
            'products__order_items__order'
        ).select_related('parent')
        
        return categories