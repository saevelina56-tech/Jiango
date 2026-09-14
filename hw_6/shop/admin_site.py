from django.contrib.admin import AdminSite


class ShopAdminSite(AdminSite):
    site_header = 'Панель управления магазином'
    site_title = 'Магазин'
    index_title = 'Управление каталогом и заказами'
    site_url = '/'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        priority = {'Order', 'Product'}
        for app in app_list:
            app['models'].sort(
                key=lambda m: (m['object_name'] not in priority, m['name'])
            )
        return app_list


shop_admin_site = ShopAdminSite(name='shop_admin')