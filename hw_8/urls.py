from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import ProductViewSet, ProductsByCategoryView, CategoryViewSet
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    
    path('', include(router.urls)),
    path('products/by-category/<slug:category_slug>/', 
         ProductsByCategoryView.as_view(), 
         name='products-by-category'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)