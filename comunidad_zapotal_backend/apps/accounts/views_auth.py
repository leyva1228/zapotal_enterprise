"""
Vistas adicionales de autenticacion: registro con OTP, verificacion,
reenvio, reset de contrasena, 2FA con TOTP, logout.

SMS / Firebase fue eliminado en la ronda 2026-06-19 v2.
OAuth (Google/Facebook) queda documentado como futuro, no expuesto en UI.
"""
import logging
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps.accounts.models import Usuario, Comunero, PendingApproval, OTPVerification
from apps.accounts.services import (
    AuthService, OTPService, EmailService, TwoFAService, TurnstileService,
)
from apps.core.utils import get_client_ip, log_audit_event

logger = logging.getLogger(__name__)


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class OTPThrottle(AnonRateThrottle):
    scope = 'otp'


class ResetPasswordThrottle(AnonRateThrottle):
    scope = 'reset_password'


# =====================================================================
# REGISTRO PUBLICO
# =====================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterThrottle])
def registro_iniciar(request):
    """
    POST /api/v1/registro/iniciar/
    Crea un Usuario en estado PENDIENTE_OTP y envia codigo por email.
    """
    data = request.data
    required = ['email', 'password', 'dni', 'nombres', 'apellidos']
    for f in required:
        if not data.get(f):
            return Response(
                {'detail': f'Campo requerido: {f}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    token = data.get('turnstile_token', '')
    # Validacion ZeroBounce del email (fail-open) — corre ANTES de Turnstile
    # para evitar que spammers consuman cuota de Turnstile con emails basura.
    from apps.comunidad.zerobounce import validar_email as zb_validar
    email = data['email'].strip().lower()
    zb_resultado = zb_validar(email, ip_address=get_client_ip(request))
    if not zb_resultado.es_valido:
        log_audit_event(
            accion='REG_ZB_BLOCK',
            ip_address=get_client_ip(request),
            metadata={
                'email_dominio': email.split('@')[1] if '@' in email else '?',
                'sub_status': zb_resultado.sub_status,
                'status': zb_resultado.status,
            },
        )
        detail = zb_resultado.motivo or 'El correo electronico no es valido.'
        if zb_resultado.did_you_mean:
            detail = f'{detail} Sugerencia: {zb_resultado.did_you_mean}.'
        return Response(
            {
                'detail': detail,
                'code': 'EMAIL_INVALID',
                'sub_status': zb_resultado.sub_status,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not TurnstileService.verify(token, get_client_ip(request)):
        return Response(
            {'detail': 'Verificacion antibot fallida.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from django.conf import settings as dj_settings
    pwd = data.get('password') or ''
    pwd_min = getattr(dj_settings, 'PASSWORD_MIN_LENGTH', 8)
    if len(pwd) < pwd_min:
        return Response(
            {'detail': f'La contrasena debe tener al menos {pwd_min} caracteres.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if getattr(dj_settings, 'PASSWORD_REQUIRE_UPPERCASE', True) and not any(c.isupper() for c in pwd):
        return Response(
            {'detail': 'La contrasena debe incluir al menos una mayuscula.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if getattr(dj_settings, 'PASSWORD_REQUIRE_DIGIT', True) and not any(c.isdigit() for c in pwd):
        return Response(
            {'detail': 'La contrasena debe incluir al menos un numero.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = email  # ya normalizado arriba despues de ZeroBounce
    existing_user = Usuario.objects.filter(email=email).first()
    if existing_user is not None:
        if existing_user.estado == Usuario.EstadoUsuario.PENDIENTE_OTP:
            # Usuario se registro pero no ingreso el codigo OTP.
            # Re-enviamos el codigo y respondemos como si fuera registro fresco.
            envio_result = OTPService.generar_y_enviar(
                usuario=existing_user,
                tipo=OTPVerification.TipoOTP.REGISTRO,
                destinatario=existing_user.email,
                ip=get_client_ip(request),
            )
            return Response({
                'usuario_id': existing_user.id,
                'canal': 'EMAIL',
                'mensaje': 'Tu cuenta esta en verificacion. Te enviamos un nuevo codigo.',
                'cooldown_reenvio': OTPService.COOLDOWN_REENVIO_SEGUNDOS,
                'dev_otp': envio_result.get('dev_otp') if envio_result.get('dev_otp') else None,
                'dev_otp_code': envio_result.get('dev_otp') if envio_result.get('dev_otp') else None,
                'resend': True,
            }, status=status.HTTP_200_OK)
        # Ya registrado y en otro estado (PENDIENTE_APROBACION, ACTIVO, etc.)
        return Response(
            {
                'detail': 'El email ya esta registrado.',
                'code': 'EMAIL_ALREADY_REGISTERED',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    dni = str(data['dni']).strip()
    if Comunero.objects.filter(dni=dni).exists():
        return Response(
            {'detail': 'El DNI ya esta registrado.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tipo = 'COMUNERO'

    with transaction.atomic():
        comunero = Comunero.objects.create(
            dni=dni,
            nombres=data['nombres'].strip(),
            apellidos=data['apellidos'].strip(),
        )
        usuario = Usuario.objects.create_user(
            email=email,
            password=data['password'],
            tipo_usuario=tipo,
            estado=Usuario.EstadoUsuario.PENDIENTE_OTP,
            comunero=comunero,
            telefono=data.get('telefono') or None,
            canal_verificacion=Usuario.CanalVerificacion.EMAIL,
        )

    envio_result = OTPService.generar_y_enviar(
        usuario=usuario,
        tipo=OTPVerification.TipoOTP.REGISTRO,
        destinatario=usuario.email,
        ip=get_client_ip(request),
    )

    log_audit_event(
        usuario=usuario,
        accion='CREATE',
        modelo_afectado='Usuario',
        objeto_id=str(usuario.id),
        descripcion='Registro publico iniciado',
        request=request,
        metadata={'tipo_usuario': tipo, 'canal': 'EMAIL'},
    )

    return Response({
        'usuario_id': usuario.id,
        'canal': 'EMAIL',
        'mensaje': 'Te enviamos un codigo de verificacion a tu correo.',
        'dev_otp_code': envio_result.get('dev_otp') if envio_result.get('dev_otp') else None,
        'cooldown_reenvio': OTPService.COOLDOWN_REENVIO_SEGUNDOS,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPThrottle])
def registro_verificar_otp(request):
    """
    POST /api/v1/registro/verificar-otp/
    Verifica el codigo OTP; pasa al estado PENDIENTE_APROBACION.
    """
    import logging
    logger = logging.getLogger(__name__)
    data = request.data
    usuario_id = data.get('usuario_id')
    codigo = data.get('codigo')
    if not usuario_id or not codigo:
        return Response({'detail': 'Faltan datos.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        OTPService.verificar(usuario, OTPVerification.TipoOTP.REGISTRO, codigo, get_client_ip(request))
    except ValidationError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        logger.exception('Error inesperado en OTPService.verificar para usuario %s: %s', usuario_id, exc)
        return Response(
            {'detail': f'Error al verificar el codigo: {type(exc).__name__}.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Si llegamos aquí, el codigo fue valido. Promover usuario.
    try:
        with transaction.atomic():
            usuario.estado = Usuario.EstadoUsuario.PENDIENTE_APROBACION
            usuario.email_verificado = True
            usuario.save(update_fields=['estado', 'email_verificado'])
            PendingApproval.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'datos_registro': {
                        'email': usuario.email,
                        'dni': usuario.comunero.dni if usuario.comunero else None,
                        'nombres': usuario.comunero.nombres if usuario.comunero else '',
                        'apellidos': usuario.comunero.apellidos if usuario.comunero else '',
                    },
                    'ip_registro': get_client_ip(request) or '0.0.0.0',
                    'user_agent_registro': (request.META.get('HTTP_USER_AGENT', '') or '')[:255],
                },
            )

        # Notificar a admins
        from apps.accounts.models import Usuario as U
        admins = U.objects.filter(tipo_usuario='ADMIN', estado='ACTIVO')
        from apps.messaging.models import Notificacion
        for admin in admins:
            Notificacion.objects.create(
                destinatario=admin,
                titulo=f'Nueva solicitud de registro: {usuario.email}',
                mensaje='Hay un nuevo usuario pendiente de aprobacion.',
                tipo=Notificacion.Tipo.INFO,
                url_destino='/admin/usuarios',
                referencia_tipo=Notificacion.ReferenciaTipo.USUARIO,
                referencia_id=usuario.id,
            )

        log_audit_event(
            usuario=usuario,
            accion='OTP_VERIFIED',
            modelo_afectado='Usuario',
            objeto_id=str(usuario.id),
            descripcion='OTP de registro verificado',
            request=request,
        )
    except Exception as exc:
        logger.exception('Error inesperado al promover usuario %s despues de OTP valido: %s', usuario_id, exc)
        return Response(
            {'detail': f'OTP valido pero fallo la activacion: {type(exc).__name__}. Contacta al administrador.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({
        'success': True,
        'estado': usuario.estado,
        'usuario_id': usuario.id,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPThrottle])
def registro_reenviar_otp(request):
    """
    POST /api/v1/registro/reenviar-otp/
    Reenvia el codigo OTP si ha pasado el cooldown (60s por defecto).
    """
    data = request.data
    usuario_id = data.get('usuario_id')
    if not usuario_id:
        return Response({'detail': 'Falta usuario_id.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        envio = OTPService.generar_y_enviar(
            usuario=usuario,
            tipo=OTPVerification.TipoOTP.REGISTRO,
            destinatario=usuario.email,
            ip=get_client_ip(request),
        )
    except ValidationError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    return Response({
        'success': True,
        'canal': 'EMAIL',
        'dev_otp_code': envio['envio_result'].get('dev_otp') if envio['envio_result'].get('dev_otp') else None,
        'cooldown_reenvio': OTPService.COOLDOWN_REENVIO_SEGUNDOS,
    })


# =====================================================================
# LOGIN + 2FA
# =====================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario_v2(request):
    """
    POST /api/v1/auth/login/
    - Si el usuario no tiene 2FA: retorna access + refresh inmediatamente.
    - Si tiene 2FA: retorna {requires_2fa: true, token_temp, usuario_id}.
    """
    from apps.accounts.views import _build_usuario_payload
    from django.core.exceptions import ValidationError as DjangoVE

    email = (request.data.get('email') or '').strip().lower()
    password = request.data.get('password') or ''
    if not email or not password:
        return Response({'detail': 'Faltan credenciales.'}, status=status.HTTP_400_BAD_REQUEST)

    user = AuthService.authenticate_user(email, password)
    if not user:
        log_audit_event(
            accion='LOGIN_FAILED', ip_address=get_client_ip(request),
            metadata={'email': email},
        )
        return Response({'detail': 'Credenciales invalidas.'}, status=status.HTTP_401_UNAUTHORIZED)

    # --- Auto-desbloqueo si bloqueo temporal expiró ---
    if user.estado == Usuario.EstadoUsuario.BLOQUEADO and user.bloqueado_hasta:
        if timezone.now() >= user.bloqueado_hasta:
            user.estado = Usuario.EstadoUsuario.ACTIVO
            user.is_active = True
            user.bloqueado_hasta = None
            user.failed_login_attempts = 0
            user.save(update_fields=['estado', 'is_active', 'bloqueado_hasta', 'failed_login_attempts'])
            logger.info('Bloqueo temporal expirado para usuario %s', user.email)

    if user.estado == Usuario.EstadoUsuario.PENDIENTE_OTP:
        return Response(
            {'detail': 'Debes verificar el codigo de registro antes de iniciar sesion.',
             'code': 'USER_PENDING_OTP'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if user.estado in (
        Usuario.EstadoUsuario.BLOQUEADO,
        Usuario.EstadoUsuario.RECHAZADO,
        Usuario.EstadoUsuario.INACTIVO,
        Usuario.EstadoUsuario.DE_BAJA,
    ):
        code_map = {
            Usuario.EstadoUsuario.BLOQUEADO: 'USER_BLOCKED',
            Usuario.EstadoUsuario.RECHAZADO: 'USER_REJECTED',
            Usuario.EstadoUsuario.INACTIVO: 'USER_INACTIVE',
            Usuario.EstadoUsuario.DE_BAJA: 'USER_DE_BAJA',
        }
        return Response(
            {'detail': 'Cuenta no habilitada.', 'code': code_map.get(user.estado)},
            status=status.HTTP_403_FORBIDDEN,
        )

    if user.two_factor_enabled:
        token_temp = AuthService.issue_short_token(user)
        return Response({
            'requires_2fa': True,
            'token_temp': token_temp,
            'usuario_id': user.id,
        }, status=status.HTTP_202_ACCEPTED)

    access, refresh = AuthService.issue_tokens(user)
    log_audit_event(
        usuario=user, accion='LOGIN', ip_address=get_client_ip(request),
        metadata={'metodo': 'password'},
    )
    return Response({
        'access': access,
        'refresh': refresh,
        'usuario': _build_usuario_payload(user),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_verify_2fa_login(request):
    """
    POST /api/v1/auth/2fa/verify-login/
    Verifica TOTP o backup code y emite tokens reales.
    """
    from apps.accounts.views import _build_usuario_payload

    token_temp = request.data.get('token_temp') or ''
    codigo = request.data.get('codigo') or ''
    if not token_temp or not codigo:
        return Response({'detail': 'Faltan datos.'}, status=status.HTTP_400_BAD_REQUEST)

    user = AuthService.validate_pre_2fa_token(token_temp)
    if not user:
        return Response({'detail': 'Token invalido o expirado.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not TwoFAService.validar(user, codigo, get_client_ip(request)):
        return Response({'detail': 'Codigo incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)

    access, refresh = AuthService.issue_tokens(user)
    log_audit_event(
        usuario=user, accion='LOGIN', ip_address=get_client_ip(request),
        metadata={'metodo': '2fa'},
    )
    return Response({
        'access': access,
        'refresh': refresh,
        'usuario': _build_usuario_payload(user),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """Invalida el refresh token (blacklist)."""
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        refresh = request.data.get('refresh') or ''
        if refresh:
            RefreshToken(refresh).blacklist()
    except TokenError:
        pass
    log_audit_event(
        usuario=request.user, accion='LOGOUT', ip_address=get_client_ip(request),
    )
    return Response({'success': True}, status=status.HTTP_205_RESET_CONTENT)


# =====================================================================
# 2FA SETUP / DISABLE
# =====================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def twofa_setup(request):
    """
    POST /api/v1/auth/2fa/setup/
    Inicia el setup: retorna {secret, otpauth_url, qr_code_base64, backup_codes}.
    NO activa 2FA; el usuario debe confirmar con un codigo en /2fa/confirm/.
    """
    user = request.user
    setup = TwoFAService.iniciar_setup(user)
    if not setup:
        return Response(
            {'detail': 'No se pudo iniciar el setup. Verifica que pyotp y qrcode esten instalados.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(setup)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def twofa_confirm(request):
    """
    POST /api/v1/auth/2fa/confirm/
    Body: {secret, codigo}. Activa 2FA tras verificar el primer codigo.
    """
    user = request.user
    secreto = request.data.get('secret') or ''
    codigo = request.data.get('codigo') or ''
    if not secreto or not codigo:
        return Response({'detail': 'Faltan datos.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = TwoFAService.confirmar_setup(user, secreto, codigo, get_client_ip(request))
    except ValidationError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    EmailService.enviar_2fa_activado(user)
    return Response({
        'success': True,
        'two_factor_enabled': True,
        'backup_codes': result['backup_codes'],
        'mensaje': '2FA activado. Guarda los codigos de respaldo en un lugar seguro.',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def twofa_disable(request):
    """POST /api/v1/auth/2fa/disable/. Body: {password}."""
    user = request.user
    password = request.data.get('password') or ''
    if not password:
        return Response({'detail': 'Falta contrasena.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        TwoFAService.desactivar(user, password, get_client_ip(request))
    except ValidationError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': True, 'two_factor_enabled': False})


# =====================================================================
# PASSWORD RESET
# =====================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ResetPasswordThrottle])
def password_reset_request(request):
    data = request.data
    email = (data.get('email') or '').strip().lower()
    if not email:
        return Response({'detail': 'Falta email.'}, status=status.HTTP_400_BAD_REQUEST)
    # Validacion ZeroBounce con anti-enumeracion: si el email es invalido,
    # retornamos 200 igual pero NO enviamos OTP.
    from apps.comunidad.zerobounce import validar_email as zb_validar
    zb_resultado = zb_validar(email, ip_address=get_client_ip(request))
    if not zb_resultado.es_valido:
        logger.info(
            'Password reset bloqueado por ZeroBounce: dominio=%s sub=%s',
            email.split('@')[1] if '@' in email else '?',
            zb_resultado.sub_status,
        )
        log_audit_event(
            accion='PASSRESET_ZB_BLOCK',
            ip_address=get_client_ip(request),
            metadata={
                'email_dominio': email.split('@')[1] if '@' in email else '?',
                'sub_status': zb_resultado.sub_status,
                'status': zb_resultado.status,
            },
        )
        # Anti-enumeracion: respuesta generica.
        return Response({'success': True, 'detail': 'Si el email existe, enviamos un codigo.'})
    user = Usuario.objects.filter(email=email).first()
    if user:
        try:
            OTPService.generar_y_enviar(
                usuario=user,
                tipo=OTPVerification.TipoOTP.RESET_PASSWORD,
                destinatario=user.email,
                ip=get_client_ip(request),
            )
        except ValidationError:
            pass
    return Response({'success': True, 'detail': 'Si el email existe, enviamos un codigo.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ResetPasswordThrottle])
def password_reset_confirm(request):
    data = request.data
    email = (data.get('email') or '').strip().lower()
    codigo = data.get('codigo') or ''
    nueva = data.get('nueva_password') or ''
    if not (email and codigo and nueva):
        return Response({'detail': 'Faltan datos.'}, status=status.HTTP_400_BAD_REQUEST)
    user = Usuario.objects.filter(email=email).first()
    if not user:
        return Response({'detail': 'Email no registrado.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        OTPService.verificar(user, OTPVerification.TipoOTP.RESET_PASSWORD, codigo, get_client_ip(request))
    except ValidationError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if len(nueva) < 8:
        return Response({'detail': 'La contrasena debe tener al menos 8 caracteres.'},
                        status=status.HTTP_400_BAD_REQUEST)
    user.set_password(nueva)
    user.last_password_change = timezone.now()
    user.save(update_fields=['password', 'last_password_change'])
    # Revocar tokens
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
    OutstandingToken.objects.filter(user=user).delete()
    log_audit_event(
        usuario=user, accion='PASSWORD_RESET',
        descripcion='Contrasena restablecida via OTP', ip_address=get_client_ip(request),
    )
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password(request, user_id=None):
    """POST /api/v1/usuarios/{id}/cambiar-password/. Body: {password_actual, password_nueva}."""
    user_id = user_id or request.data.get('usuario_id') or request.user.id
    user = request.user if user_id == request.user.id else Usuario.objects.filter(id=user_id).first()
    if not user or user.id != request.user.id:
        return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)
    actual = request.data.get('password_actual') or ''
    nueva = request.data.get('password_nueva') or ''
    if not user.check_password(actual):
        return Response({'detail': 'Contrasena actual incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(nueva) < 8:
        return Response({'detail': 'La nueva contrasena debe tener al menos 8 caracteres.'},
                        status=status.HTTP_400_BAD_REQUEST)
    user.set_password(nueva)
    user.last_password_change = timezone.now()
    user.password_reset_required = False
    user.save(update_fields=['password', 'last_password_change', 'password_reset_required'])
    EmailService.enviar_cambio_password(user)
    return Response({'success': True})
