from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop.admin_site import shop_admin_site

urlpatterns = [
    path('admin/', shop_admin_site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)