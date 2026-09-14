from django.urls import path
from shop.admin_site import shop_admin_site

urlpatterns = [
    path('admin/', shop_admin_site.urls),
]