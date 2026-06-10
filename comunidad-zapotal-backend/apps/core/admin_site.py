from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomAdminSite(AdminSite):
    site_header = "Comunidad Zapotal"
    site_title = "Panel de Administración"
    index_title = _("Bienvenido al Panel de Administración")
    site_url = "/"  # Enlace "Ver sitio"
    
    # Logo personalizado
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'site_logo': '/static/img/zapotal-logo.png',
            'site_logo_width': 40,
            'site_logo_height': 40,
        })
        return context
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        # Filtrar para mostrar solo apps que queremos
        apps_to_show = ['comunidad', 'content', 'messaging', 'reports']
        
        # Opcional: Reordenar apps
        filtered_app_list = [
            app for app in app_list 
            if app['app_label'] in apps_to_show
        ]
        
        return filtered_app_list
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        # Puedes agregar URLs personalizadas aquí si quieres
        return urls

# Crear instancia del admin custom
custom_admin_site = CustomAdminSite(name='custom_admin')
