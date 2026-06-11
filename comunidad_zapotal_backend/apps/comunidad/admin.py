from django.contrib import admin
from .models import Autoridad
from apps.core.admin_site import custom_admin_site


@admin.register(Autoridad, site=custom_admin_site)
class AutoridadAdmin(admin.ModelAdmin):
    list_display = ['cargo', 'periodo', 'comunero', 'fecha_inicio', 'fecha_fin', 'activa']
    list_filter = ['cargo', 'periodo', 'fecha_inicio']
    search_fields = ['cargo', 'comunero__nombres', 'comunero__apellidos', 'comunero__dni']
    ordering = ['-fecha_inicio']
    date_hierarchy = 'fecha_inicio'
    raw_id_fields = ['comunero', 'usuario']
    list_per_page = 25

    def activa(self, obj):
        """Indica si la autoridad está actualmente en funciones."""
        from django.utils import timezone
        hoy = timezone.now().date()
        if obj.fecha_fin and obj.fecha_fin < hoy:
            return '❌ Finalizó'
        return '✅ Activa'
    activa.short_description = 'Estado actual'

    actions = ['exportar_csv']

    @admin.action(description='Exportar a CSV')
    def exportar_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="autoridades_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Cargo', 'Periodo', 'Nombres', 'Apellidos', 'DNI', 'Fecha inicio', 'Fecha fin'])

        for a in queryset:
            writer.writerow([
                a.id, a.cargo, a.periodo,
                a.comunero.nombres, a.comunero.apellidos, a.comunero.dni,
                a.fecha_inicio, a.fecha_fin or '',
            ])

        return response
