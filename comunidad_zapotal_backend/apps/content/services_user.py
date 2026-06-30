"""Servicios para solicitudes de baja de cuenta."""
import logging
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from apps.accounts.models import Usuario
from apps.accounts.services import EmailService
from apps.core.utils import log_audit_event
from apps.messaging.models import Notificacion
from .models import SolicitudBaja

logger = logging.getLogger(__name__)


class BajaService:
    """Operaciones sobre solicitudes de baja y cuentas."""

    GRACE_HOURS = getattr(settings, 'BAJA_GRACE_HOURS', 0)

    @classmethod
    def _notificar_admin_baja(cls, solicitud):
        """Notifica a todos los admins sobre una nueva solicitud de baja."""
        admins = Usuario.objects.filter(
            Q(is_superuser=True) | (Q(tipo_usuario='ADMIN') & Q(estado='ACTIVO')),
        ).distinct()
        Notificacion.objects.bulk_create([
            Notificacion(
                destinatario=a,
                titulo=f'Solicitud de baja de {solicitud.usuario.email}',
                mensaje=f'Motivo: {solicitud.motivo}',
                tipo=Notificacion.Tipo.NUEVA_SOLICITUD_BAJA,
                url_destino='/admin/bajas',
                referencia_tipo=Notificacion.ReferenciaTipo.SOLICITUD_BAJA,
                referencia_id=solicitud.id,
            )
            for a in admins
        ])

    @classmethod
    def crear_solicitud(cls, usuario, motivo):
        """Crea una nueva solicitud de baja y envía notificaciones."""
        solicitud = SolicitudBaja.objects.create(usuario=usuario, motivo=motivo)
        EmailService.enviar_solicitud_baja(usuario)
        cls._notificar_admin_baja(solicitud)
        return solicitud

    @classmethod
    def cancelar_solicitud(cls, usuario):
        """Cancela una solicitud PENDIENTE del usuario."""
        solicitud = SolicitudBaja.objects.filter(
            usuario=usuario,
            estado=SolicitudBaja.EstadoSolicitud.PENDIENTE,
        ).first()
        if not solicitud:
            return None
        solicitud.estado = SolicitudBaja.EstadoSolicitud.CANCELADA
        solicitud.fecha_revision = timezone.now()
        solicitud.save(update_fields=['estado', 'fecha_revision'])
        return solicitud

    @classmethod
    def asignar_en_revision(cls, solicitud_id, admin_user):
        """Marca una solicitud como EN_REVISION (la toma un admin)."""
        try:
            solicitud = SolicitudBaja.objects.select_related('usuario').get(id=solicitud_id)
        except SolicitudBaja.DoesNotExist:
            return None, 'Solicitud no encontrada.'
        if solicitud.estado != SolicitudBaja.EstadoSolicitud.PENDIENTE:
            return None, f'Solicitud ya procesada (estado: {solicitud.estado}).'
        solicitud.estado = SolicitudBaja.EstadoSolicitud.EN_REVISION
        solicitud.fecha_revision = timezone.now()
        solicitud.revisado_por = admin_user
        solicitud.save(update_fields=['estado', 'fecha_revision', 'revisado_por'])
        return solicitud, None

    @classmethod
    def aprobar_solicitud(cls, solicitud_id, admin_user, notas=''):
        """Aprueba una solicitud de baja: cambia estado, desactiva usuario, notifica."""
        try:
            solicitud = SolicitudBaja.objects.select_related('usuario').get(id=solicitud_id)
        except SolicitudBaja.DoesNotExist:
            return None, 'Solicitud no encontrada.'
        if solicitud.estado not in (
            SolicitudBaja.EstadoSolicitud.PENDIENTE,
            SolicitudBaja.EstadoSolicitud.EN_REVISION,
        ):
            return None, f'Solicitud ya procesada (estado: {solicitud.estado}).'
        with transaction.atomic():
            solicitud.estado = SolicitudBaja.EstadoSolicitud.APROBADA
            solicitud.fecha_revision = timezone.now()
            solicitud.revisado_por = admin_user
            solicitud.notas_admin = notas
            solicitud.save()
            solicitud.usuario.estado = Usuario.EstadoUsuario.DE_BAJA
            solicitud.usuario.is_active = False
            solicitud.usuario.bloqueado_hasta = None
            solicitud.usuario.save(update_fields=['estado', 'is_active', 'bloqueado_hasta'])
        Notificacion.objects.create(
            destinatario=solicitud.usuario,
            titulo='Solicitud de baja aprobada',
            mensaje='Tu cuenta ha sido dada de baja. Ya no puedes iniciar sesion.',
            tipo=Notificacion.Tipo.SOLICITUD_BAJA_APROBADA,
            url_destino='/cuenta/bloqueada',
            referencia_tipo=Notificacion.ReferenciaTipo.SOLICITUD_BAJA,
            referencia_id=solicitud.id,
        )
        logger.info(
            'Baja aprobada por admin %s para usuario %s (solicitud %d)',
            admin_user.email, solicitud.usuario.email, solicitud.id,
        )
        return solicitud, None

    @classmethod
    def rechazar_solicitud(cls, solicitud_id, admin_user, notas=''):
        """Rechaza una solicitud de baja."""
        try:
            solicitud = SolicitudBaja.objects.select_related('usuario').get(id=solicitud_id)
        except SolicitudBaja.DoesNotExist:
            return None, 'Solicitud no encontrada.'
        if solicitud.estado not in (
            SolicitudBaja.EstadoSolicitud.PENDIENTE,
            SolicitudBaja.EstadoSolicitud.EN_REVISION,
        ):
            return None, f'Solicitud ya procesada (estado: {solicitud.estado}).'
        with transaction.atomic():
            solicitud.estado = SolicitudBaja.EstadoSolicitud.RECHAZADA
            solicitud.fecha_revision = timezone.now()
            solicitud.revisado_por = admin_user
            solicitud.notas_admin = notas
            solicitud.save()
        Notificacion.objects.create(
            destinatario=solicitud.usuario,
            titulo='Solicitud de baja rechazada',
            mensaje=f'Tu solicitud de baja fue rechazada. {("Motivo: " + notas) if notas else "Contacta al administrador para mas informacion."}',
            tipo=Notificacion.Tipo.SOLICITUD_BAJA_RECHAZADA,
            url_destino='/perfil?tab=info',
            referencia_tipo=Notificacion.ReferenciaTipo.SOLICITUD_BAJA,
            referencia_id=solicitud.id,
        )
        logger.info(
            'Baja rechazada por admin %s para usuario %s (solicitud %d)',
            admin_user.email, solicitud.usuario.email, solicitud.id,
        )
        return solicitud, None

    @classmethod
    def auto_procesar_solicitud(cls, solicitud):
        """Procesa automaticamente una solicitud PENDIENTE si expiro el plazo de gracia."""
        if cls.GRACE_HOURS <= 0:
            return False
        delta = timezone.now() - solicitud.fecha_solicitud
        if delta.total_seconds() < cls.GRACE_HOURS * 3600:
            return False
        with transaction.atomic():
            solicitud.estado = SolicitudBaja.EstadoSolicitud.APROBADA
            solicitud.fecha_revision = timezone.now()
            solicitud.save(update_fields=['estado', 'fecha_revision'])
            solicitud.usuario.estado = Usuario.EstadoUsuario.DE_BAJA
            solicitud.usuario.is_active = False
            solicitud.usuario.bloqueado_hasta = None
            solicitud.usuario.save(update_fields=['estado', 'is_active', 'bloqueado_hasta'])
        logger.info(
            'Baja auto-procesada para usuario %s (solicitud %d)',
            solicitud.usuario.email, solicitud.id,
        )
        return True

    @classmethod
    def procesar_pendientes_vencidas(cls, usuario=None):
        """Busca solicitudes PENDIENTE vencidas y las procesa automaticamente."""
        qs = SolicitudBaja.objects.filter(
            estado=SolicitudBaja.EstadoSolicitud.PENDIENTE,
        ).select_related('usuario')
        if usuario:
            qs = qs.filter(usuario=usuario)
        count = 0
        for s in qs:
            if cls.auto_procesar_solicitud(s):
                count += 1
        return count
