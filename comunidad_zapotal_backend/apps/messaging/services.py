"""
Service layer para el módulo de mensajería.
"""
import logging

from django.contrib.auth import get_user_model

from .models import Mensaje, Notificacion

logger = logging.getLogger(__name__)


class MensajeService:
    """Servicio para gestión de mensajes privados."""

    @staticmethod
    def enviar_mensaje(remitente, destinatario, contenido: str) -> Mensaje:
        """
        Envía un mensaje y crea una notificación para el destinatario.

        Raises:
            ValueError: Si remitente == destinatario
        """
        if remitente.id == destinatario.id:
            raise ValueError('No puedes enviarte mensajes a ti mismo.')

        mensaje = Mensaje.objects.create(
            remitente=remitente,
            destinatario=destinatario,
            contenido=contenido,
        )
        Notificacion.objects.create(
            destinatario=destinatario,
            titulo=f'Nuevo mensaje de {remitente.email}',
            mensaje=contenido[:100],
            tipo='mensaje',
        )
        logger.info('Mensaje enviado de %s a %s', remitente.email, destinatario.email)
        return mensaje

    @staticmethod
    def marcar_leido(mensaje: Mensaje, usuario) -> Mensaje:
        """Marca un mensaje como leído."""
        if mensaje.destinatario_id != usuario.id:
            raise PermissionError('Solo el destinatario puede marcar como leído.')
        mensaje.leido = True
        mensaje.save(update_fields=['leido'])
        return mensaje


class NotificacionService:
    """Servicio para gestión de notificaciones."""

    @staticmethod
    def crear_notificacion(destinatario, titulo: str, mensaje: str, tipo: str = 'info') -> Notificacion:
        notif = Notificacion.objects.create(
            destinatario=destinatario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
        )
        logger.info('Notificación creada para %s: %s', destinatario.email, titulo)
        return notif

    @staticmethod
    def marcar_todas_leidas(usuario) -> int:
        """Marca todas las notificaciones del usuario como leídas."""
        count = Notificacion.objects.filter(destinatario=usuario, leido=False).update(leido=True)
        return count


def notificar_todos_los_admins(
    tipo: str, titulo: str, mensaje: str, url_destino: str = '',
) -> int:
    """V2.2: crea una notificacion para cada admin activo del sistema.

    Utilizado por comandos automaticos (cron) que necesitan
    informar a todos los administradores (ej. reclamos vencidos).

    Returns: cantidad de notificaciones creadas.
    """
    User = get_user_model()
    admins = User.objects.filter(
        tipo_usuario='ADMIN', estado='ACTIVO', is_active=True,
    )
    notifs = [
        Notificacion(
            destinatario=a,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            url_destino=url_destino[:2000] if url_destino else '',
        )
        for a in admins
    ]
    created = Notificacion.objects.bulk_create(notifs)
    logger.info(
        '%d notificacion(es) creadas para admins (tipo=%s)',
        len(created), tipo,
    )
    return len(created)
