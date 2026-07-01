"""
Signals del modulo comunidad (V2.3).

- post_delete: limpia notificaciones huerfanas (MensajeContacto).
- post_save / post_delete: mantiene la galeria sincronizada con
  Noticias y Eventos que tienen imagen.
"""
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


# ── Helpers ──────────────────────────────────────────────────────────

def _imagen_presente(instance):
    """Retorna True si la instancia tiene una imagen (local o externa)."""
    return bool(instance.imagen or instance.imagen_url)


def _categoria_galeria_desde(instance):
    """Mapea Categoria.nombre de content a GaleriaImagen.Categoria.

    Si instance no tiene categoria o el nombre no coincide, retorna COMUNIDAD.
    """
    from .models_institucionales import GaleriaImagen as GI
    nombre = instance.categoria.nombre if instance.categoria_id else ''
    for choice_key, choice_label in GI.Categoria.choices:
        if nombre.upper() == choice_key:
            return choice_key
        if nombre.lower() == choice_label.lower():
            return choice_key
        if nombre.lower().replace(' ', '') == choice_label.lower().replace(' ', ''):
            return choice_key
    return GI.Categoria.COMUNIDAD


def _asignar_orden_si_nuevo(gi, created):
    """Asigna orden autoincremental si el registro es nuevo (created=True).

    update_or_create no pasa por save(), por eso se hace explicito.
    """
    if created:
        max_orden = type(gi).objects.aggregate(models.Max('orden'))['orden__max'] or 0
        gi.orden = max_orden + 1
        gi.save(update_fields=['orden'])


def _sincronizar_galeria_para_noticia(noticia):
    """Crea/actualiza un registro de GaleriaImagen para una Noticia."""
    from .models_institucionales import GaleriaImagen as GI
    if not _imagen_presente(noticia):
        GI.objects.filter(noticia=noticia).delete()
        return
    defaults = {
        'titulo': noticia.titulo,
        'imagen_url_externa': noticia.imagen_url,
        'categoria': _categoria_galeria_desde(noticia),
        'fecha': noticia.fecha_publicacion.date(),
        'activo': True,
    }
    if noticia.imagen:
        defaults['imagen'] = noticia.imagen
    gi, created = GI.objects.update_or_create(
        noticia=noticia,
        defaults=defaults,
    )
    _asignar_orden_si_nuevo(gi, created)


def _sincronizar_galeria_para_evento(evento):
    """Crea/actualiza un registro de GaleriaImagen para un Evento."""
    from .models_institucionales import GaleriaImagen as GI
    if not _imagen_presente(evento):
        GI.objects.filter(evento=evento).delete()
        return
    defaults = {
        'titulo': evento.titulo,
        'imagen_url_externa': evento.imagen_url,
        'categoria': _categoria_galeria_desde(evento),
        'fecha': evento.fecha.date(),
        'activo': True,
    }
    if evento.imagen:
        defaults['imagen'] = evento.imagen
    gi, created = GI.objects.update_or_create(
        evento=evento,
        defaults=defaults,
    )
    _asignar_orden_si_nuevo(gi, created)


# ── MensajeContacto ──────────────────────────────────────────────────

@receiver(post_delete, sender='comunidad.MensajeContacto')
def limpiar_notifs_de_mensaje_contacto(sender, instance, **kwargs):
    """Al eliminar un MensajeContacto, eliminar las notificaciones
    con referencia_tipo='CONTACTO' y referencia_id=instance.id."""
    from apps.messaging.models import Notificacion
    Notificacion.objects.filter(
        referencia_tipo='CONTACTO',
        referencia_id=instance.id,
    ).delete()


# ── Galeria - Noticia ────────────────────────────────────────────────

@receiver(post_save, sender='content.Noticia')
def galeria_crear_actualizar_por_noticia(sender, instance, **kwargs):
    """Al crear/actualizar una Noticia con imagen, crear o actualizar
    la entrada correspondiente en GaleriaImagen.

    Si la noticia pierde su imagen, se elimina la entrada de galeria.
    """
    _sincronizar_galeria_para_noticia(instance)


@receiver(post_delete, sender='content.Noticia')
def galeria_eliminar_por_noticia(sender, instance, **kwargs):
    """Al eliminar una Noticia, eliminar su entrada de galeria."""
    from .models_institucionales import GaleriaImagen
    GaleriaImagen.objects.filter(noticia=instance).delete()


# ── Galeria - Evento ─────────────────────────────────────────────────

@receiver(post_save, sender='content.Evento')
def galeria_crear_actualizar_por_evento(sender, instance, **kwargs):
    """Al crear/actualizar un Evento con imagen, crear o actualizar
    la entrada correspondiente en GaleriaImagen."""
    _sincronizar_galeria_para_evento(instance)


@receiver(post_delete, sender='content.Evento')
def galeria_eliminar_por_evento(sender, instance, **kwargs):
    """Al eliminar un Evento, eliminar su entrada de galeria."""
    from .models_institucionales import GaleriaImagen
    GaleriaImagen.objects.filter(evento=instance).delete()
