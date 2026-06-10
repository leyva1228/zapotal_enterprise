from django.contrib import admin
from .models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'estado', 'fecha_publicacion']
    list_filter = ['estado', 'categoria']
    search_fields = ['titulo', 'contenido']
    date_hierarchy = 'fecha_publicacion'

    def get_date_hierarchy(self):
        try:
            return super().get_date_hierarchy()
        except ValueError as e:
            if 'time zone' in str(e).lower():
                return None
            raise



@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'estado', 'fecha_evento']
    list_filter = ['estado', 'categoria']
    search_fields = ['titulo', 'descripcion']


@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'noticia', 'evento', 'orden']
    list_filter = ['tipo']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'contenido', 'estado', 'fecha']
    list_filter = ['estado']
    search_fields = ['contenido']


@admin.register(Reaccion)
class ReaccionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'noticia', 'evento']
    list_filter = ['tipo']
