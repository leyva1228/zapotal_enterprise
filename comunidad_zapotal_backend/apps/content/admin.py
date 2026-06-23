"""
Admin customizado para el módulo de contenido.

Incluye:
- Inlines (Noticia → Multimedia, Comentarios)
- Custom actions (exportar CSV, cambiar estado batch)
- Filtros mejorados con date_hierarchy
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from apps.core.admin_site import custom_admin_site
from .models import (
    Categoria, Noticia, Evento, Multimedia,
    Comentario, Reaccion,
)


class MultimediaInline(admin.TabularInline):
    """Inline para mostrar archivos multimedia de una noticia."""
    model = Multimedia
    extra = 1
    fields = ['tipo', 'archivo']
    verbose_name = 'Archivo multimedia'
    verbose_name_plural = 'Archivos multimedia'


class ComentarioInline(admin.TabularInline):
    """Inline para mostrar comentarios de una noticia."""
    model = Comentario
    extra = 0
    fields = ['autor', 'contenido', 'estado', 'fecha']
    readonly_fields = ['fecha']
    show_change_link = True
    max_num = 20
    verbose_name = 'Comentario'
    verbose_name_plural = 'Comentarios'


@admin.register(Categoria, site=custom_admin_site)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_creacion', 'total_noticias']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

    def total_noticias(self, obj):
        return obj.noticias.count()
    total_noticias.short_description = 'N° Noticias'


@admin.register(Noticia, site=custom_admin_site)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'estado', 'fecha_publicacion', 'vistas', 'autor_display']
    list_filter = ['estado', 'categoria', 'fecha_publicacion']
    search_fields = ['titulo', 'contenido', 'resumen']
    ordering = ['-fecha_publicacion']
    readonly_fields = ['fecha_publicacion', 'vistas']
    raw_id_fields = ['categoria']
    inlines = [MultimediaInline, ComentarioInline]
    list_per_page = 25
    save_on_top = True

    fieldsets = (
        (None, {'fields': ('titulo', 'resumen', 'contenido')}),
        ('Clasificación', {'fields': ('estado', 'categoria')}),
        ('Imagen', {'fields': ('imagen',)}),
        ('Metadata', {'fields': ('fecha_publicacion', 'vistas'), 'classes': ('collapse',)}),
    )

    actions = ['publicar_noticias', 'archivar_noticias', 'exportar_csv']

    def autor_display(self, obj):
        """Placeholder para futuro autor automático."""
        return '—'
    autor_display.short_description = 'Autor'

    @admin.action(description='Publicar noticias seleccionadas')
    def publicar_noticias(self, request, queryset):
        updated = queryset.update(estado='PUBLICADA')
        self.message_user(request, f'{updated} noticia(s) publicada(s).')

    @admin.action(description='Archivar noticias seleccionadas')
    def archivar_noticias(self, request, queryset):
        updated = queryset.update(estado='ARCHIVADA')
        self.message_user(request, f'{updated} noticia(s) archivada(s).')

    @admin.action(description='Exportar a CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="noticias_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Título', 'Categoría', 'Estado', 'Vistas', 'Fecha'])

        for n in queryset:
            writer.writerow([
                n.id, n.titulo, n.categoria.nombre if n.categoria else '',
                n.estado, n.vistas, n.fecha_publicacion,
            ])

        return response


@admin.register(Evento, site=custom_admin_site)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha', 'lugar']
    list_filter = ['fecha', 'lugar']
    search_fields = ['titulo', 'descripcion', 'lugar']
    ordering = ['-fecha']
    list_per_page = 25


@admin.register(Multimedia, site=custom_admin_site)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ['archivo', 'tipo', 'noticia', 'evento', 'fecha_subida']
    list_filter = ['tipo', 'fecha_subida']
    search_fields = ['archivo']
    raw_id_fields = ['noticia', 'evento']
    list_per_page = 30


@admin.register(Comentario, site=custom_admin_site)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'noticia', 'estado', 'fecha', 'editado']
    list_filter = ['estado', 'fecha']
    search_fields = ['contenido', 'autor__email', 'noticia__titulo']
    ordering = ['-fecha']
    raw_id_fields = ['noticia', 'autor', 'respuesta_a']
    readonly_fields = ['fecha']
    list_per_page = 30

    actions = ['aprobar_comentarios', 'ocultar_comentarios', 'marcar_eliminados']

    @admin.action(description='Aprobar comentarios seleccionados')
    def aprobar_comentarios(self, request, queryset):
        updated = queryset.update(estado='PUBLICADO')
        self.message_user(request, f'{updated} comentario(s) aprobado(s).')

    @admin.action(description='Ocultar comentarios seleccionados')
    def ocultar_comentarios(self, request, queryset):
        updated = queryset.update(estado='OCULTO')
        self.message_user(request, f'{updated} comentario(s) ocultado(s).')

    @admin.action(description='Marcar como eliminados (soft delete)')
    def marcar_eliminados(self, request, queryset):
        updated = queryset.update(estado='ELIMINADO')
        self.message_user(request, f'{updated} comentario(s) marcado(s) como eliminado(s).')


@admin.register(Reaccion, site=custom_admin_site)
class ReaccionAdmin(admin.ModelAdmin):
    list_display = ['noticia', 'autor', 'tipo', 'fecha']
    list_filter = ['tipo', 'fecha']
    search_fields = ['noticia__titulo', 'autor__email']
    raw_id_fields = ['noticia', 'autor']
    list_per_page = 50
