from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductsByCategoryView


router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'categories/<slug:slug>/products/',
        ProductsByCategoryView.as_view(),
        name='products-by-category',
    ),
]