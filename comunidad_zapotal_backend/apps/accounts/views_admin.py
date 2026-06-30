"""
Vistas administrativas: aprobacion, rechazo, bloqueo, listado de pendientes.
"""
import logging
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from apps.accounts.models import Usuario, PendingApproval
from apps.accounts.services import EmailService
from apps.accounts.serializers import PendingApprovalSerializer, UsuarioSerializer
from apps.core.permissions import IsAdminUser
from apps.core.utils import get_client_ip, log_audit_event

logger = logging.getLogger(__name__)


class IsAdminOrSelf(IsAdminUser):
    """Placeholder: usa IsAdminUser; permite mas adelante granularidad."""


@api_view(['GET'])
@permission_classes([IsAdminUser])
def pending_users(request):
    """GET /api/v1/usuarios/pendientes/"""
    qs = Usuario.objects.filter(
        estado=Usuario.EstadoUsuario.PENDIENTE_APROBACION,
    ).select_related('comunero').order_by('-fecha_registro')
    data = []
    for u in qs:
        pending = getattr(u, 'pending_approval', None)
        data.append({
            'usuario_id': u.id,
            'email': u.email,
            'dni': u.dni,
            'nombre_completo': u.nombre_completo,
            'tipo_usuario': u.tipo_usuario,
            'fecha_registro': u.fecha_registro,
            'oauth_provider': u.proveedor_oauth or '',
            'datos_registro': pending.datos_registro if pending else {},
            'ip_registro': pending.ip_registro if pending else '',
        })
    return Response({'results': data, 'count': len(data)})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_user(request, user_id):
    """POST /api/v1/usuarios/{id}/aprobar/"""
    try:
        usuario = Usuario.objects.select_related('comunero').get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # Bloquear aprobacion si el usuario no ha completado la verificacion OTP
    if usuario.estado == Usuario.EstadoUsuario.PENDIENTE_OTP:
        log_audit_event(
            usuario=request.user,
            accion='APPROVE_FAILED',
            modelo_afectado='Usuario',
            objeto_id=str(usuario.id),
            descripcion=f'Intento de aprobacion fallido: {usuario.email} aun no completo OTP',
            request=request,
            metadata={'estado_actual': usuario.estado, 'motivo': 'USER_NOT_VERIFIED'},
        )
        return Response(
            {
                'detail': 'El usuario aun no completo la verificacion OTP. No se puede aprobar.',
                'code': 'USER_NOT_VERIFIED',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if usuario.estado not in (
        Usuario.EstadoUsuario.PENDIENTE_OTP,
        Usuario.EstadoUsuario.PENDIENTE_APROBACION,
    ):
        return Response(
            {'detail': f'El usuario no esta en estado de aprobacion (actual: {usuario.estado}).'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    notas = request.data.get('notas_admin', '')
    with transaction.atomic():
        usuario.estado = Usuario.EstadoUsuario.ACTIVO
        usuario.is_active = True
        usuario.aprobado_por = request.user
        usuario.fecha_aprobacion = timezone.now()
        usuario.save(update_fields=[
            'estado', 'is_active', 'aprobado_por', 'fecha_aprobacion',
        ])
        pending = getattr(usuario, 'pending_approval', None)
        if pending:
            pending.revisado_por = request.user
            pending.fecha_revision = timezone.now()
            pending.notas_admin = notas
            pending.save(update_fields=[
                'revisado_por', 'fecha_revision', 'notas_admin',
            ])

    # Email de bienvenida
    EmailService.enviar_bienvenida(usuario.email, usuario.nombre_completo)

    # Notificacion in-app
    from apps.messaging.models import Notificacion
    Notificacion.objects.create(
        destinatario=usuario,
        titulo='Cuenta aprobada',
        mensaje='Tu cuenta ha sido aprobada. Ya puedes iniciar sesion con tu correo y la contrasena que registraste.',
        tipo=Notificacion.Tipo.APROBACION_CUENTA,
        url_destino='/login',
        referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
        referencia_id=usuario.id,
    )

    log_audit_event(
        usuario=request.user,
        accion='APPROVE',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion=f'Usuario {usuario.email} aprobado',
        request=request,
        metadata={'notas_admin': notas},
    )
    return Response({'status': 'ok', 'estado': usuario.estado})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_user(request, user_id):
    """POST /api/v1/usuarios/{id}/rechazar/"""
    try:
        usuario = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    motivo = (request.data.get('motivo') or '').strip()
    usuario.estado = Usuario.EstadoUsuario.RECHAZADO
    usuario.is_active = False
    usuario.motivo_rechazo = motivo
    usuario.save(update_fields=['estado', 'is_active', 'motivo_rechazo'])

    pending = getattr(usuario, 'pending_approval', None)
    if pending:
        pending.revisado_por = request.user
        pending.fecha_revision = timezone.now()
        pending.notas_admin = motivo
        pending.save(update_fields=['revisado_por', 'fecha_revision', 'notas_admin'])

    EmailService.enviar_rechazo(usuario.email, motivo)

    from apps.messaging.models import Notificacion
    Notificacion.objects.create(
        destinatario=usuario,
        titulo='Registro no aprobado',
        mensaje=f'Motivo: {motivo or "No especificado"}',
        tipo=Notificacion.Tipo.RECHAZO_CUENTA,
        url_destino='/perfil?tab=info',
        referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
        referencia_id=usuario.id,
    )

    log_audit_event(
        usuario=request.user,
        accion='REJECT',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion=f'Usuario {usuario.email} rechazado',
        request=request,
        metadata={'motivo': motivo},
    )
    return Response({'status': 'ok', 'estado': usuario.estado})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def block_user(request, user_id):
    """
    POST /api/v1/usuarios/{id}/bloquear/
    Body opcional: {motivo, dias_bloqueo}
    - Si se pasa `dias_bloqueo` (int > 0), el bloqueo es temporal y se
      auto-desbloqueará al cumplir el plazo (controlado en login).
    """
    try:
        usuario = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.estado == Usuario.EstadoUsuario.DE_BAJA:
        return Response(
            {'detail': 'No se puede bloquear una cuenta que ya fue dada de baja.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    motivo = (request.data.get('motivo') or '').strip()
    dias_bloqueo = request.data.get('dias_bloqueo')
    if dias_bloqueo is not None:
        try:
            dias = int(dias_bloqueo)
        except (ValueError, TypeError):
            return Response({'detail': 'dias_bloqueo debe ser un numero entero.'}, status=status.HTTP_400_BAD_REQUEST)
        if dias <= 0:
            return Response({'detail': 'dias_bloqueo debe ser mayor a 0.'}, status=status.HTTP_400_BAD_REQUEST)
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > timezone.now():
            current_delta = usuario.bloqueado_hasta - timezone.now()
            usuario.bloqueado_hasta = timezone.now() + current_delta + timezone.timedelta(days=dias)
        else:
            usuario.bloqueado_hasta = timezone.now() + timezone.timedelta(days=dias)

    usuario.estado = Usuario.EstadoUsuario.BLOQUEADO
    usuario.is_active = False
    update_flds = ['estado', 'is_active']
    if dias_bloqueo is not None:
        update_flds.append('bloqueado_hasta')
    usuario.save(update_fields=update_flds)

    # Revocar todos los tokens
    OutstandingToken.objects.filter(user=usuario).delete()

    from apps.messaging.models import Notificacion
    Notificacion.objects.create(
        destinatario=usuario,
        titulo='Cuenta bloqueada',
        mensaje=f'Tu cuenta ha sido bloqueada. Motivo: {motivo or "No especificado"}',
        tipo=Notificacion.Tipo.CUENTA_BLOQUEADA,
        url_destino='/cuenta/bloqueada',
        referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
        referencia_id=usuario.id,
    )

    log_audit_event(
        usuario=request.user,
        accion='BLOCK',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion=f'Usuario {usuario.email} bloqueado',
        request=request,
        metadata={'motivo': motivo},
    )
    return Response({'status': 'ok', 'estado': usuario.estado})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def unblock_user(request, user_id):
    """POST /api/v1/usuarios/{id}/desbloquear/"""
    try:
        usuario = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.estado == Usuario.EstadoUsuario.DE_BAJA:
        return Response(
            {'detail': 'No se puede desbloquear una cuenta que fue dada de baja permanentemente.',
             'code': 'USER_DE_BAJA'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario.estado = Usuario.EstadoUsuario.ACTIVO
    usuario.is_active = True
    usuario.failed_login_attempts = 0
    usuario.locked_until = None
    usuario.bloqueado_hasta = None
    usuario.save(update_fields=[
        'estado', 'is_active', 'failed_login_attempts', 'locked_until', 'bloqueado_hasta',
    ])

    from apps.messaging.models import Notificacion
    Notificacion.objects.create(
        destinatario=usuario,
        titulo='Cuenta desbloqueada',
        mensaje='Tu cuenta ha sido desbloqueada. Ya puedes iniciar sesion.',
        tipo=Notificacion.Tipo.CUENTA_DESBLOQUEADA,
        url_destino='/login',
        referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
        referencia_id=usuario.id,
    )

    log_audit_event(
        usuario=request.user,
        accion='UNBLOCK',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion=f'Usuario {usuario.email} desbloqueado',
        request=request,
    )
    return Response({'status': 'ok', 'estado': usuario.estado})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def dar_baja_usuario(request, user_id):
    """POST /api/v1/usuarios/{id}/dar-baja/

    Da de baja permanentemente a un usuario activo. No requiere
    SolicitudBaja -- es accion directa del admin.
    """
    try:
        usuario = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.estado == Usuario.EstadoUsuario.DE_BAJA:
        return Response(
            {'detail': 'El usuario ya esta dado de baja.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    notas = (request.data.get('motivo') or '').strip()

    usuario.estado = Usuario.EstadoUsuario.DE_BAJA
    usuario.is_active = False
    usuario.bloqueado_hasta = None
    usuario.save(update_fields=['estado', 'is_active', 'bloqueado_hasta'])

    OutstandingToken.objects.filter(user=usuario).delete()

    EmailService.enviar_baja_aprobada(usuario, notas)

    from apps.messaging.models import Notificacion
    Notificacion.objects.create(
        destinatario=usuario,
        titulo='Cuenta dada de baja',
        mensaje=f'Tu cuenta ha sido dada de baja por un administrador.{(" Motivo: " + notas) if notas else ""}',
        tipo=Notificacion.Tipo.SOLICITUD_BAJA_APROBADA,
        url_destino='/cuenta/bloqueada',
        referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
        referencia_id=usuario.id,
    )

    log_audit_event(
        usuario=request.user,
        accion='DAR_BAJA',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion=f'Usuario {usuario.email} dado de baja por admin',
        request=request,
        metadata={'motivo': notas},
    )
    return Response({'status': 'ok', 'estado': usuario.estado})
