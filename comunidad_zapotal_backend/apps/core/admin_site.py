from django.contrib.admin import AdminSite


class ZapotalAdminSite(AdminSite):
    site_header = 'Zapotal Admin'
    site_title = 'Administración Zapotal'
    index_title = 'Panel de Administración'
    site_url = '/api/'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        ordering = {
            'Cuentas': 1,
            'Contenido': 2,
            'Comunidad': 3,
            'Mensajería': 4,
            'Reportes': 5,
        }
        app_list.sort(key=lambda x: ordering.get(x.get('name', ''), 99))
        return app_list


custom_admin_site = ZapotalAdminSite(name='zapotal_admin')