from django.contrib import admin
from .models import Mensaje, Notificacion
from apps.core.admin_site import custom_admin_site


@admin.register(Mensaje, site=custom_admin_site)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['remitente', 'destinatario', 'fecha', 'leido']
    list_filter = ['leido', 'fecha']
    search_fields = ['remitente__email', 'destinatario__email', 'contenido']
    ordering = ['-fecha']
    raw_id_fields = ['remitente', 'destinatario']
    readonly_fields = ['fecha']
    list_per_page = 30


@admin.register(Notificacion, site=custom_admin_site)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'destinatario', 'tipo', 'fecha', 'leido']
    list_filter = ['tipo', 'leido', 'fecha']
    search_fields = ['titulo', 'mensaje', 'destinatario__email']
    ordering = ['-fecha']
    raw_id_fields = ['destinatario']
    readonly_fields = ['fecha']
    list_per_page = 30
