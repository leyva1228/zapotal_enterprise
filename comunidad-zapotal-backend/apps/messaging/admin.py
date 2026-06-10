from django.contrib import admin
from .models import Mensaje, Notificacion


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['asunto', 'remitente', 'destinatario', 'leido', 'fecha_envio']
    list_filter = ['leido', 'estado']
    search_fields = ['asunto', 'cuerpo', 'remitente__email', 'destinatario__email']



@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'leido', 'fecha']
    list_filter = ['tipo', 'leido']
    search_fields = ['titulo', 'mensaje']
