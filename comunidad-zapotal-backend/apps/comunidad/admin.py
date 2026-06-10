from django.contrib import admin
from .models import Comunero, Autoridad


@admin.register(Comunero)
class ComuneroAdmin(admin.ModelAdmin):
    list_display = ['nombres', 'apellidos', 'dni', 'estado', 'fecha_registro']
    list_filter = ['estado']
    search_fields = ['nombres', 'apellidos', 'dni']
    ordering = ['apellidos', 'nombres']


@admin.register(Autoridad)
class AutoridadAdmin(admin.ModelAdmin):
    list_display = ['comunero', 'cargo', 'estado', 'fecha_inicio', 'fecha_fin']
    list_filter = ['cargo', 'estado']
    search_fields = ['comunero__nombres', 'comunero__apellidos']
