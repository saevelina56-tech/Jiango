from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductsByCategoryView, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    
    path('products/by-category/<slug:category_slug>/', 
         ProductsByCategoryView.as_view(), 
         name='products-by-category'),
]