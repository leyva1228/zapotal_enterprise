"""
Admin customizado para el módulo de cuentas (Usuario y Comunero).
"""
import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpResponse
from django.utils import timezone
from .models import Usuario, Comunero
from apps.core.admin_site import custom_admin_site


@admin.register(Usuario, site=custom_admin_site)
class UsuarioAdmin(DjangoUserAdmin):
    """
    Admin para el modelo Usuario custom.
    """
    list_display = ['email', 'tipo_usuario', 'estado', 'is_active', 'is_staff', 'fecha_registro']
    list_filter = ['tipo_usuario', 'estado', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'comunero__nombres', 'comunero__apellidos', 'comunero__dni']
    ordering = ['-fecha_registro']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('comunero', 'foto_perfil')}),
        ('Permisos y rol', {
            'fields': (
                'tipo_usuario', 'estado',
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            )
        }),
        ('Fechas importantes', {'fields': ('last_login', 'fecha_registro')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'tipo_usuario', 'comunero', 'estado',
                'is_staff', 'is_superuser',
            ),
        }),
    )
    readonly_fields = ['fecha_registro', 'last_login']
    raw_id_fields = ['comunero']
    list_per_page = 30

    actions = ['activar_usuarios', 'desactivar_usuarios', 'exportar_csv']

    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        updated = queryset.update(estado='ACTIVO', is_active=True)
        self.message_user(request, f'{updated} usuario(s) activado(s).')

    @admin.action(description='Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        updated = queryset.update(estado='INACTIVO', is_active=False)
        self.message_user(request, f'{updated} usuario(s) desactivado(s).')

    @admin.action(description='Exportar a CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="usuarios_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Tipo', 'Estado', 'Nombres', 'Apellidos', 'DNI', 'Fecha registro'])

        for u in queryset:
            nombres = u.comunero.nombres if u.comunero else ''
            apellidos = u.comunero.apellidos if u.comunero else ''
            dni = u.comunero.dni if u.comunero else ''
            writer.writerow([
                u.id, u.email, u.tipo_usuario, u.estado,
                nombres, apellidos, dni, u.fecha_registro,
            ])

        return response


@admin.register(Comunero, site=custom_admin_site)
class ComuneroAdmin(admin.ModelAdmin):
    list_display = ['nombres', 'apellidos', 'dni', 'estado', 'nombre_completo']
    list_filter = ['estado']
    search_fields = ['nombres', 'apellidos', 'dni']
    ordering = ['apellidos', 'nombres']
    list_per_page = 30

    fieldsets = (
        ('Datos personales', {'fields': ('dni', 'nombres', 'apellidos', 'estado')}),
    )
