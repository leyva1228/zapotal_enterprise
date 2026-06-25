from django.contrib import admin
from .models import LibroReclamacion
from apps.core.admin_site import custom_admin_site


@admin.register(LibroReclamacion, site=custom_admin_site)
class LibroReclamacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'tipo', 'estado', 'fecha']
    list_filter = ['estado', 'tipo', 'fecha']
    search_fields = ['nombre', 'email', 'descripcion']
    ordering = ['-fecha']
    readonly_fields = ['fecha']
    list_per_page = 30

    fieldsets = (
        ('Datos del consumidor', {
            'fields': ('nombre', 'email', 'telefono', 'direccion')
        }),
        ('Reclamo', {
            'fields': ('tipo', 'descripcion', 'estado')
        }),
        ('Metadata', {
            'fields': ('fecha',),
            'classes': ('collapse',)
        }),
    )

    actions = ['marcar_en_proceso', 'marcar_resuelto', 'exportar_csv']

    @admin.action(description='Marcar como "En proceso"')
    def marcar_en_proceso(self, request, queryset):
        updated = queryset.update(estado='EN_PROCESO')
        self.message_user(request, f'{updated} reclamo(s) marcado(s) en proceso.')

    @admin.action(description='Marcar como "Resuelto"')
    def marcar_resuelto(self, request, queryset):
        updated = queryset.update(estado='RESUELTO')
        self.message_user(request, f'{updated} reclamo(s) marcado(s) como resuelto.')

    @admin.action(description='Exportar a CSV')
    def exportar_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="reclamos_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Fecha', 'Nombre', 'Email', 'Teléfono', 'Tipo', 'Estado', 'Descripción'])

        for r in queryset:
            writer.writerow([
                r.id, r.fecha, r.nombre, r.email, r.telefono, r.tipo, r.estado,
                r.descripcion[:100] + '...' if len(r.descripcion) > 100 else r.descripcion,
            ])

        return response
