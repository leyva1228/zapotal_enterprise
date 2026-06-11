"""
Señales (signals) de Django para implementar Domain Events.

Permiten desacoplar side effects del código de negocio principal.
"""
import logging
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# === Noticia ===
@receiver(post_save, sender='content.Noticia')
def noticia_creada_o_actualizada(sender, instance, created, **kwargs):
    """Log cuando se crea o actualiza una noticia."""
    if created:
        logger.info(
            'Noticia creada: id=%s titulo="%s" estado=%s',
            instance.id, instance.titulo, instance.estado
        )
    else:
        logger.debug('Noticia actualizada: id=%s', instance.id)


@receiver(post_delete, sender='content.Noticia')
def noticia_eliminada(sender, instance, **kwargs):
    """Log cuando se elimina una noticia."""
    logger.warning('Noticia eliminada: id=%s titulo="%s"', instance.id, instance.titulo)


# === Comentario ===
@receiver(post_save, sender='content.Comentario')
def comentario_creado(sender, instance, created, **kwargs):
    """
    Cuando se crea un comentario, podríamos notificar al autor de la noticia.
    Por ahora solo log.
    """
    if created and instance.noticia_id:
        logger.info(
            'Comentario en noticia %s por autor_id=%s',
            instance.noticia_id, instance.autor_id
        )


# === Reacción ===
@receiver(post_save, sender='content.Reaccion')
def reaccion_creada_o_actualizada(sender, instance, created, **kwargs):
    """Log de reacciones."""
    if created:
        logger.info(
            'Reacción creada: noticia_id=%s tipo=%s autor_id=%s',
            instance.noticia_id, instance.tipo, instance.autor_id
        )


@receiver(post_delete, sender='content.Reaccion')
def reaccion_eliminada(sender, instance, **kwargs):
    """Log de reacción eliminada (toggle off)."""
    logger.info('Reacción eliminada: noticia_id=%s autor_id=%s', instance.noticia_id, instance.autor_id)


# === Mensaje ===
@receiver(post_save, sender='messaging.Mensaje')
def mensaje_enviado(sender, instance, created, **kwargs):
    """Log de mensaje enviado."""
    if created:
        logger.info(
            'Mensaje enviado: id=%s de=%s a=%s',
            instance.id, instance.remitente_id, instance.destinatario_id
        )


# === Notificación ===
@receiver(post_save, sender='messaging.Notificacion')
def notificacion_creada(sender, instance, created, **kwargs):
    """Log de notificación creada."""
    if created:
        logger.info(
            'Notificación creada: destinatario_id=%s tipo=%s titulo="%s"',
            instance.destinatario_id, instance.tipo, instance.titulo
        )


# === Usuario ===
@receiver(post_save, sender='accounts.Usuario')
def usuario_creado_o_actualizado(sender, instance, created, **kwargs):
    """Log de cambios en usuarios."""
    if created:
        logger.info(
            'Usuario creado: id=%s email=%s tipo=%s',
            instance.id, instance.email, instance.tipo_usuario
        )
    else:
        logger.debug('Usuario actualizado: id=%s', instance.id)


# === LibroReclamacion ===
@receiver(post_save, sender='reports.LibroReclamacion')
def reclamacion_creada_o_actualizada(sender, instance, created, **kwargs):
    """Log de reclamos - crítico para INDECOPI compliance."""
    if created:
        logger.info(
            'LibroReclamacion creado: id=%s tipo=%s nombre=%s',
            instance.id, instance.tipo, instance.nombre
        )
    else:
        logger.info(
            'LibroReclamacion actualizado: id=%s estado=%s',
            instance.id, instance.estado
        )
