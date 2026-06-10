from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Usuario,
    Comunero,
    Categoria,
    Noticia,
    Evento,
    Comentario,
    Reaccion,
    Mensaje,
    Notificacion,
    Multimedia,
    Autoridad,
    ContactoMensaje,
)


# =========================
# REGISTROS BÁSICOS
# =========================

admin.site.register(Usuario)
admin.site.register(Comunero)
admin.site.register(Categoria)
admin.site.register(Noticia)
admin.site.register(Evento)
admin.site.register(Comentario)
admin.site.register(Reaccion)
admin.site.register(Mensaje)
admin.site.register(Notificacion)
admin.site.register(Multimedia)


# =========================
# AUTORIDADES
# =========================

@admin.register(Autoridad)
class AutoridadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "mostrar_foto",
        "nombres",
        "apellidos",
        "cargo",
        "telefono",
        "correo",
        "estado",
        "orden",
    )

    list_filter = (
        "estado",
        "cargo",
    )

    search_fields = (
        "nombres",
        "apellidos",
        "cargo",
        "correo",
    )

    ordering = (
        "orden",
        "cargo",
    )

    readonly_fields = (
        "fecha_registro",
        "preview_foto",
    )

    fieldsets = (

        ("Información personal", {
            "fields": (
                "nombres",
                "apellidos",
                "cargo",
                "descripcion",
            )
        }),

        ("Contacto", {
            "fields": (
                "telefono",
                "correo",
            )
        }),

        ("Imagen", {
            "fields": (
                "foto",
                "preview_foto",
            )
        }),

        ("Configuración", {
            "fields": (
                "orden",
                "estado",
                "fecha_registro",
            )
        }),
    )

    def mostrar_foto(self, obj):

        if obj.foto:

            return format_html(
                '<img src="{}" width="45" height="45" style="border-radius:50%; object-fit:cover;" />',
                obj.foto.url
            )

        return "Sin foto"

    mostrar_foto.short_description = "Foto"

    def preview_foto(self, obj):

        if obj.foto:

            return format_html(
                '<img src="{}" width="220" style="border-radius:12px;" />',
                obj.foto.url
            )

        return "No hay imagen"

    preview_foto.short_description = "Vista previa"


# =========================
# CONTACTO
# =========================

@admin.register(ContactoMensaje)
class ContactoMensajeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombres",
        "correo",
        "telefono",
        "asunto",
        "estado",
        "fecha_envio",
    )

    list_filter = (
        "estado",
        "fecha_envio",
    )

    search_fields = (
        "nombres",
        "correo",
        "asunto",
        "mensaje",
    )

    readonly_fields = (
        "fecha_envio",
    )

    ordering = (
        "-fecha_envio",
    )

    fieldsets = (

        ("Información del remitente", {
            "fields": (
                "nombres",
                "correo",
                "telefono",
            )
        }),

        ("Mensaje", {
            "fields": (
                "asunto",
                "mensaje",
            )
        }),

        ("Estado", {
            "fields": (
                "estado",
                "fecha_envio",
            )
        }),
    )




    from django.contrib import admin
from .models import LibroReclamacion


@admin.register(LibroReclamacion)
class LibroReclamacionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombres_completos",
        "tipo_solicitud",
        "asunto",
        "estado",
        "fecha_registro",
    )

    list_filter = (
        "tipo_solicitud",
        "estado",
        "fecha_registro",
    )

    search_fields = (
        "nombres",
        "apellidos",
        "dni",
        "correo",
        "asunto",
    )

    readonly_fields = (
        "fecha_registro",
    )

    ordering = (
        "-fecha_registro",
    )

    fieldsets = (

        ("Información personal", {
            "fields": (
                "nombres",
                "apellidos",
                "dni",
                "correo",
                "telefono",
            )
        }),

        ("Información de la solicitud", {
            "fields": (
                "tipo_solicitud",
                "asunto",
                "descripcion",
                "pedido",
                "estado",
            )
        }),

        ("Registro", {
            "fields": (
                "fecha_registro",
            )
        }),

    )

    def nombres_completos(self, obj):
        return f"{obj.nombres} {obj.apellidos}"

    nombres_completos.short_description = "Solicitante"