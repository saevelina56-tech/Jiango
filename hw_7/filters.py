import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    
    price_min = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        label="Минимальная цена"
    )
    price_max = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        label="Максимальная цена"
    )
    
    in_stock = django_filters.BooleanFilter(
        method='filter_in_stock',
        label="В наличии"
    )
    
    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'is_available': ['exact'],
        }
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0, is_available=True)
        return queryset