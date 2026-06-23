from django.contrib import admin
from apps.core.admin_site import custom_admin_site
from .models import Donacion


class DonacionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'monto', 'estado', 'destinatario', 'anonima',
        'nombre_display', 'mp_payment_id', 'mp_payment_method',
        'created_at', 'aprobado_at',
    ]
    list_filter = ['estado', 'destinatario', 'anonima', 'created_at', 'mp_payment_method']
    search_fields = [
        'id', 'mp_payment_id', 'nombre_donante', 'email_donante',
        'documento_donante', 'usuario__email', 'usuario__dni',
    ]
    readonly_fields = [
        'id', 'usuario', 'mp_payment_id', 'mp_status', 'mp_status_detail',
        'mp_payment_method', 'mp_payment_type', 'mp_installments', 'mp_raw_response',
        'ip_origen', 'user_agent', 'created_at', 'updated_at', 'aprobado_at', 'reembolsado_at',
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Donante', {
            'fields': ('usuario', 'nombre_donante', 'email_donante', 'documento_donante'),
        }),
        ('Donacion', {
            'fields': ('monto', 'moneda', 'mensaje', 'anonima', 'destinatario'),
        }),
        ('Estado', {
            'fields': ('estado', 'estado_detalle', 'aprobado_at', 'reembolsado_at'),
        }),
        ('Mercado Pago', {
            'fields': (
                'mp_payment_id', 'mp_status', 'mp_status_detail',
                'mp_payment_method', 'mp_payment_type', 'mp_installments',
                'mp_raw_response',
            ),
            'classes': ('collapse',),
        }),
        ('Origen', {
            'fields': ('ip_origen', 'user_agent'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


admin.site.register(Donacion, DonacionAdmin)
custom_admin_site.register(Donacion, DonacionAdmin)
