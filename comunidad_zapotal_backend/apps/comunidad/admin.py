from django.contrib import admin
from .models import Autoridad, ComiteComunal
from .models_institucionales import (
    ConfiguracionComunidad, MarcoLegalItem, PaginaLegal,
    HitoHistorico, GaleriaImagen, MensajeContacto,
)
from apps.core.admin_site import custom_admin_site


@admin.register(ConfiguracionComunidad, site=custom_admin_site)
class ConfiguracionComunidadAdmin(admin.ModelAdmin):
    list_display = ['nombre_oficial', 'distrito', 'provincia', 'region', 'actualizado_en']
    fieldsets = (
        ('Identidad', {
            'fields': ('nombre_oficial', 'nombre_corto', 'eslogan',
                       'descripcion_corta', 'descripcion_larga')
        }),
        ('Historia e identidad', {
            'fields': ('historia_html', 'mision', 'vision', 'valores')
        }),
        ('Ubicacion', {
            'fields': ('distrito', 'provincia', 'region', 'ubigeo',
                       'direccion_casa_comunal', 'coordenadas_lat', 'coordenadas_lng',
                       'codigo_postal')
        }),
        ('Contacto', {
            'fields': ('telefono_fijo', 'telefono_emergencias', 'whatsapp_numero',
                       'email_contacto', 'email_privacidad', 'email_denuncias',
                       'horario_atencion')
        }),
        ('Multimedia', {
            'fields': ('logo_url', 'foto_casa_comunal_url')
        }),
    )

    def has_add_permission(self, request):
        # Singleton: solo se permite crear el primer registro
        return not ConfiguracionComunidad.objects.exists()


@admin.register(MarcoLegalItem, site=custom_admin_site)
class MarcoLegalItemAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'norma', 'icono', 'orden', 'activo']
    list_filter = ['activo']
    search_fields = ['titulo', 'norma', 'descripcion']
    list_editable = ['orden', 'activo']
    ordering = ['orden', 'id']


@admin.register(PaginaLegal, site=custom_admin_site)
class PaginaLegalAdmin(admin.ModelAdmin):
    list_display = ['slug', 'titulo', 'version', 'fecha_vigencia', 'activo', 'fecha_actualizacion']
    list_filter = ['activo', 'slug']
    search_fields = ['titulo', 'contenido']
    readonly_fields = ['fecha_actualizacion']


@admin.register(HitoHistorico, site=custom_admin_site)
class HitoHistoricoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha', 'anio', 'orden', 'activo']
    list_filter = ['activo']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['orden', 'activo']
    ordering = ['orden', '-anio', '-fecha']


@admin.register(GaleriaImagen, site=custom_admin_site)
class GaleriaImagenAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'fecha', 'orden', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['orden', 'activo']
    ordering = ['orden', '-fecha']


@admin.register(MensajeContacto, site=custom_admin_site)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'asunto', 'leido', 'respondido', 'fecha']
    list_filter = ['leido', 'respondido']
    search_fields = ['nombre', 'email', 'asunto', 'mensaje']
    readonly_fields = ['fecha', 'ip_origen', 'user_agent']
    actions = ['marcar_leido', 'marcar_respondido']

    @admin.action(description='Marcar como leido')
    def marcar_leido(self, request, queryset):
        queryset.update(leido=True)

    @admin.action(description='Marcar como respondido')
    def marcar_respondido(self, request, queryset):
        queryset.update(respondido=True)


@admin.register(Autoridad, site=custom_admin_site)
class AutoridadAdmin(admin.ModelAdmin):
    list_display = ['cargo', 'nivel_gobierno', 'periodo', 'comunero', 'sexo', 'es_cargo_tradicional', 'activa']
    list_filter = ['nivel_gobierno', 'cargo_tipo', 'periodo', 'fecha_inicio', 'sexo', 'es_cargo_tradicional']
    search_fields = ['cargo', 'comunero__nombres', 'comunero__apellidos', 'comunero__dni', 'dni', 'nro_partida_sunarp']
    ordering = ['-fecha_inicio']
    raw_id_fields = ['comunero', 'usuario', 'autoridad_anterior']
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
        writer.writerow(['ID', 'Cargo', 'Nivel', 'Periodo', 'Nombres', 'Apellidos', 'DNI', 'Sexo', 'Fecha inicio', 'Fecha fin'])

        for a in queryset:
            writer.writerow([
                a.id, a.cargo, a.nivel_gobierno, a.periodo,
                a.comunero.nombres if a.comunero else '', a.comunero.apellidos if a.comunero else '',
                a.dni, a.sexo,
                a.fecha_inicio, a.fecha_fin or '',
            ])

        return response


@admin.register(ComiteComunal, site=custom_admin_site)
class ComiteComunalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'nivel', 'fecha_constitucion', 'periodo_fin', 'activo']
    list_filter = ['tipo', 'nivel', 'activo', 'fecha_constitucion']
    search_fields = ['nombre', 'descripcion']
    raw_id_fields = ['presidente', 'secretario', 'vocal']
    ordering = ['-fecha_constitucion']
    list_per_page = 25
