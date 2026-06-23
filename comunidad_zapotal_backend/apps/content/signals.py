"""
Signals para crear notificaciones automaticas al publicar contenido.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Noticia, Evento
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
        tipo='NUEVA_NOTICIA',
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
        tipo='NUEVO_EVENTO',
        excluir_superuser=True,
    ))


def _bulk_notificar(titulo, mensaje, tipo, excluir_superuser=False):
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
        )
        for u in destinatarios
    ])
    logger.info('Notificacion bulk creada: %s -> %d usuarios', tipo, len(destinatarios))
