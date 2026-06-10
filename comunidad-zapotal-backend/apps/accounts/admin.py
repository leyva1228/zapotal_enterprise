from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'get_full_name', 'dni', 'tipo_usuario', 'is_active']
    list_filter = ['tipo_usuario', 'is_active', 'dni_verificado']
    search_fields = ['email', 'first_name', 'last_name', 'dni']
    ordering = ['email']
