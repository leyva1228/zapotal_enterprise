"""
Signals para crear notificaciones automaticas al publicar contenido.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Noticia, Evento, Comentario
from apps.accounts.models import Usuario
from apps.messaging.models import Notificacion

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Noticia)
def notificar_nueva_noticia(sender, instance, created, **kwargs):
    """Al crear una noticia PUBLICADA, notifica a todos los usuarios activos."""
    if not created:
        return
    if instance.estado != Noticia.EstadoNoticia.PUBLICADA:
        return
    transaction.on_commit(lambda: _bulk_notificar(
        titulo=f'Nueva noticia: {instance.titulo}',
        mensaje=f'Se ha publicado una nueva noticia en {instance.categoria.nombre if instance.categoria else "Comunidad"}.',
        tipo='nueva_noticia',
        url_destino=f'/noticias/{instance.id}',
        referencia_tipo='NOTICIA',
        referencia_id=instance.id,
        excluir_superuser=True,
    ))


@receiver(post_save, sender=Evento)
def notificar_nuevo_evento(sender, instance, created, **kwargs):
    """Al crear un evento, notifica a todos los usuarios activos."""
    if not created:
        return
    transaction.on_commit(lambda: _bulk_notificar(
        titulo=f'Nuevo evento: {instance.titulo}',
        mensaje=f'Se ha programado un nuevo evento para el {instance.fecha.strftime("%d/%m/%Y") if instance.fecha else "proximamente"}.',
        tipo='nuevo_evento',
        url_destino=f'/eventos/{instance.id}',
        referencia_tipo='EVENTO',
        referencia_id=instance.id,
        excluir_superuser=True,
    ))


@receiver(post_save, sender=Comentario)
def notificar_comentario_moderado(sender, instance, created, **kwargs):
    """Loop 3.8: notifica al autor cuando su comentario es moderado.

    Solo se dispara en update (created=False) y cuando el estado es OCULTO
    (moderacion: el admin oculto el comentario por incumplir normas).
    """
    if created:
        return
    if instance.estado != Comentario.EstadoComentario.OCULTO:
        return
    if not instance.autor_id:
        return  # sin autor, no se puede notificar
    titulo = 'Tu comentario fue moderado'
    mensaje = (
        f'Tu comentario en "{instance.noticia.titulo if instance.noticia_id else "el post"}" '
        f'fue ocultado por el equipo de moderacion por incumplir las normas de la comunidad.'
    )
    url_destino = f'/noticias/{instance.noticia_id}' if instance.noticia_id else '/'
    Notificacion.objects.create(
        destinatario_id=instance.autor_id,
        titulo=titulo,
        mensaje=mensaje,
        tipo='comentario_moderado',
        url_destino=url_destino,
        referencia_tipo='COMENTARIO',
        referencia_id=instance.id,
    )
    logger.info('Notificacion comentario moderado creada: autor_id=%s comentario_id=%s', instance.autor_id, instance.id)


def _bulk_notificar(titulo, mensaje, tipo, url_destino='', referencia_tipo='', referencia_id=None, excluir_superuser=False):
    """Crea notificaciones en bulk para usuarios activos."""
    qs = Usuario.objects.filter(estado=Usuario.EstadoUsuario.ACTIVO, is_active=True)
    if excluir_superuser:
        qs = qs.exclude(is_superuser=True)
    destinatarios = list(qs)
    if not destinatarios:
        return
    Notificacion.objects.bulk_create([
        Notificacion(
            destinatario=u,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            url_destino=url_destino,
            referencia_tipo=referencia_tipo,
            referencia_id=referencia_id,
        )
        for u in destinatarios
    ])
    logger.info('Notificacion bulk creada: %s -> %d usuarios', tipo, len(destinatarios))
