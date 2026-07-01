"""
Service layer para el modulo de cuentas.

Centraliza logica de negocio relacionada con usuarios, comuneros, autoridades,
OTP, email y 2FA con TOTP.

Nota: SMS / Firebase fue eliminado en la ronda 2026-06-19 v2. Solo email
via Resend/SMTP para OTP.
"""
import logging
import secrets
import io
import hashlib
import base64
from datetime import timedelta
from typing import Optional, Tuple

from django.db import transaction
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone

from .models import Usuario, Comunero, OTPVerification

logger = logging.getLogger(__name__)


# =====================================================================
# AUTH SERVICE
# =====================================================================

class AuthService:
    """Servicio de autenticacion de usuarios."""

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario por email y password.

        Returns:
            Usuario si las credenciales son validas y el usuario esta activo.
            None en caso contrario.
        """
        if not email or not password:
            return None

        user = authenticate(username=email, password=password)
        if not user:
            logger.warning('Authentication failed for email=%s', email)
            return None

        if user.estado not in (
            Usuario.EstadoUsuario.ACTIVO,
            Usuario.EstadoUsuario.PENDIENTE_OTP,
            Usuario.EstadoUsuario.PENDIENTE_APROBACION,
        ):
            logger.warning('Authentication attempt on inactive user=%s', email)
            return None

        logger.info('User authenticated: %s', email)
        return user

    @staticmethod
    def issue_tokens(user: Usuario) -> Tuple[str, str]:
        """Genera tokens JWT (access + refresh) para un usuario."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    @staticmethod
    def issue_short_token(user: Usuario) -> str:
        """Genera un token temporal de 5 minutos usado durante el paso 2FA."""
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.tokens import AccessToken
        access = AccessToken()
        access['user_id'] = user.id
        access['scope'] = 'pre_2fa'
        access.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=5))
        return str(access)

    @staticmethod
    def validate_pre_2fa_token(token: str) -> Optional[Usuario]:
        """Valida token temporal pre-2FA y devuelve el usuario."""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access = AccessToken(token)
            if access.get('scope') != 'pre_2fa':
                return None
            user_id = access.get('user_id')
            return Usuario.objects.filter(id=user_id).first()
        except Exception:
            return None


# =====================================================================
# USUARIO SERVICE
# =====================================================================

class UsuarioService:
    """Servicio para gestion de usuarios."""

    @staticmethod
    @transaction.atomic
    def create_user_with_comunero(
        email: str,
        password: str,
        tipo_usuario: str,
        comunero_data: Optional[dict] = None,
    ) -> Usuario:
        if tipo_usuario == Usuario.TipoUsuario.COMUNERO and not comunero_data:
            raise ValueError('COMUNERO debe tener datos de comunero asociado.')

        comunero = None
        if comunero_data:
            comunero = Comunero.objects.create(**comunero_data)

        user = Usuario.objects.create_user(
            email=email,
            password=password,
            tipo_usuario=tipo_usuario,
            comunero=comunero,
        )
        logger.info('User created: %s (%s)', email, tipo_usuario)
        return user

    @staticmethod
    @transaction.atomic
    def change_password(user: Usuario, new_password: str) -> None:
        if len(new_password) < 6:
            raise ValueError('La contrasena debe tener minimo 6 caracteres.')
        user.set_password(new_password)
        user.save(update_fields=['password'])
        logger.info('Password changed for user=%s', user.email)

    @staticmethod
    def activate(user: Usuario) -> Usuario:
        user.estado = Usuario.EstadoUsuario.ACTIVO
        user.is_active = True
        user.save(update_fields=['estado', 'is_active'])
        return user

    @staticmethod
    def deactivate(user: Usuario) -> Usuario:
        user.estado = Usuario.EstadoUsuario.INACTIVO
        user.is_active = False
        user.save(update_fields=['estado', 'is_active'])
        return user


# =====================================================================
# COMUNERO SERVICE
# =====================================================================

class ComuneroService:
    @staticmethod
    @transaction.atomic
    def create_comunero(dni: str, nombres: str, apellidos: str, **extra) -> Comunero:
        comunero = Comunero.objects.create(
            dni=dni, nombres=nombres, apellidos=apellidos, **extra
        )
        logger.info('Comunero created: %s %s (DNI=%s)', nombres, apellidos, dni)
        return comunero


# =====================================================================
# EMAIL SERVICE (Resend / SMTP)
# =====================================================================

def _html_wrapper(header, paragraphs, extra_html='', warning=''):
    body_rows = ''
    for p in paragraphs:
        body_rows += (
            f'<p style="color:#555;margin:0 0 16px;font-size:15px;line-height:1.5">{p}</p>'
        )
    warning_row = (
        f'<p style="color:#b91c1c;margin:16px 0 0;font-size:14px;line-height:1.5">'
        f'⚠ {warning}</p>'
    ) if warning else ''
    return (
        f'<!DOCTYPE html>'
        f'<html><head><meta charset="utf-8"></head>'
        f'<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Inter,Arial,Helvetica,sans-serif">'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8;padding:24px 0">'
        f'<tr><td align="center">'
        f'<table role="presentation" width="520" cellpadding="0" cellspacing="0" '
        f'style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb">'
        f'<tr><td style="background:linear-gradient(135deg,#0a3d1f 0%,#1a7a42 100%);padding:24px;text-align:center">'
        f'<h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:600;letter-spacing:0.5px">'
        f'Comunidad Campesina Niño Dios de Zapotal</h1>'
        f'<p style="color:#b8d4c4;margin:4px 0 0;font-size:13px">Plataforma Institucional</p>'
        f'</td></tr>'
        f'<tr><td style="padding:32px 32px 16px">'
        f'<h2 style="color:#0a3d1f;margin:0 0 16px;font-size:18px">{header}</h2>'
        f'{body_rows}'
        f'{extra_html}'
        f'{warning_row}'
        f'</td></tr>'
        f'<tr><td style="background:#f9fafb;padding:20px 32px;border-top:1px solid #e5e7eb">'
        f'<p style="color:#999;margin:0;font-size:12px;line-height:1.5">'
        f'Comunidad Campesina Niño Dios de Zapotal<br>'
        f'<a href="https://comunidadzapotal.com" style="color:#1a7a42;text-decoration:none">'
        f'www.comunidadzapotal.com</a>'
        f'</p></td></tr>'
        f'</table></td></tr></table></body></html>'
    )


class EmailService:
    """Servicio de email transaccional."""

    @staticmethod
    def _from_email():
        return getattr(
            settings, 'DEFAULT_FROM_EMAIL',
            getattr(settings, 'RESEND_FROM_EMAIL', 'onboarding@resend.dev'),
        )

    @staticmethod
    def _is_dev():
        """Solo es "dev" si DEBUG=True Y no hay API key de Resend configurada.
        Si hay API key, SIEMPRE se envia email real aunque DEBUG=True."""
        if bool(getattr(settings, 'DEBUG', False)):
            resend_key = getattr(settings, 'RESEND_API_KEY', '')
            anymail_key = getattr(settings, 'ANYMAIL_RESEND_API_KEY', '')
            return not (resend_key or anymail_key)
        return False

    @staticmethod
    def _has_real_email_backend():
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        return 'console' not in backend and 'locmem' not in backend

    @staticmethod
    def _add_deliverability_headers(msg, destinatario):
        """Mejora la entregabilidad agregando headers estandar:
        - Reply-To: para que el usuario pueda responder.
        - List-Unsubscribe: RFC 8058, clave para no caer en spam.
        - X-Entity-ID: identificador unico del mensaje.
        """
        msg.extra_headers = msg.extra_headers or {}
        msg.extra_headers['Reply-To'] = 'no-reply@comunidadzapotal.com'
        # List-Unsubscribe: <mailto:unsubscribe@comunidadzapotal.com>, <URL>
        msg.extra_headers['List-Unsubscribe'] = (
            '<mailto:unsubscribe@comunidadzapotal.com>, '
            '<https://comunidadzapotal.com/api/v1/unsubscribe?email='
            f'{destinatario}>'
        )
        msg.extra_headers['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
        msg.extra_headers['X-Entity-ID'] = 'comunidad-zapotal-comunitarias'
        msg.extra_headers['X-Mailer'] = 'Comunidad Zapotal Platform'
        msg.extra_headers['Precedence'] = 'bulk'
        return msg

    @staticmethod
    def enviar_otp(destinatario, codigo, tipo='REGISTRO'):
        subject_map = {
            'REGISTRO': 'Tu codigo de verificacion - Comunidad Zapotal',
            'RESET_PASSWORD': 'Restablecer contrasena - Comunidad Zapotal',
            'TWO_FA': 'Codigo de verificacion en dos pasos - Comunidad Zapotal',
        }
        subject = subject_map.get(tipo, 'Notificacion - Comunidad Zapotal')
        from_email = EmailService._from_email()
        body = (
            f'Hola,\n\n'
            f'Tu codigo de verificacion es: {codigo}\n\n'
            f'Valido por 10 minutos.\n'
            f'Nunca compartas este codigo con nadie.\n\n'
            f'---\n'
            f'Comunidad Campesina Niño Dios de Zapotal\n'
            f'www.comunidadzapotal.com\n\n'
            f'Recibiste este correo porque solicitaste un codigo de acceso '
            f'en nuestra plataforma. Si no realizaste esta solicitud, '
            f'ignora este mensaje.'
        )
        html_body = (
            f'<!DOCTYPE html>'
            f'<html><head><meta charset="utf-8"></head>'
            f'<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Inter,Arial,Helvetica,sans-serif">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8;padding:24px 0">'
            f'<tr><td align="center">'
            f'<table role="presentation" width="520" cellpadding="0" cellspacing="0" '
            f'style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb">'
            # Header con branding
            f'<tr><td style="background:linear-gradient(135deg,#0a3d1f 0%,#1a7a42 100%);padding:24px;text-align:center">'
            f'<h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:600;letter-spacing:0.5px">Comunidad Campesina Niño Dios de Zapotal</h1>'
            f'<p style="color:#b8d4c4;margin:4px 0 0;font-size:13px">Plataforma Institucional</p>'
            f'</td></tr>'
            # Body
            f'<tr><td style="padding:32px 32px 16px">'
            f'<h2 style="color:#0a3d1f;margin:0 0 8px;font-size:18px">Tu codigo de verificacion</h2>'
            f'<p style="color:#555;margin:0 0 24px;font-size:15px;line-height:1.5">'
            f'Usa el siguiente codigo para completar tu solicitud. '
            f'Es valido por los proximos <strong>10 minutos</strong>.'
            f'</p>'
            # Codigo
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;border:2px dashed #b8972a;border-radius:8px;margin:24px 0">'
            f'<tr><td align="center" style="padding:24px 16px">'
            f'<span style="font-family:Courier New,monospace;font-size:36px;font-weight:700;'
            f'color:#0a3d1f;letter-spacing:8px">{codigo}</span>'
            f'</td></tr>'
            f'</table>'
            f'<p style="color:#666;margin:24px 0;font-size:14px;line-height:1.5">'
            f'Por tu seguridad, nunca compartas este codigo con nadie. '
            f'El equipo de Comunidad Zapotal jamas te lo pedira.'
            f'</p>'
            f'</td></tr>'
            # Footer
            f'<tr><td style="background:#f9fafb;padding:20px 32px;border-top:1px solid #e5e7eb">'
            f'<p style="color:#999;margin:0;font-size:12px;line-height:1.5">'
            f'Comunidad Campesina Niño Dios de Zapotal<br>'
            f'<a href="https://comunidadzapotal.com" style="color:#1a7a42;text-decoration:none">www.comunidadzapotal.com</a><br><br>'
            f'No respondas a este correo. Si no solicitaste este codigo, '
            f'puedes <a href="https://comunidadzapotal.com/api/v1/unsubscribe?email={destinatario}" '
            f'style="color:#1a7a42">cancelar la suscripcion</a>.'
            f'</p>'
            f'</td></tr>'
            f'</table>'
            f'</td></tr>'
            f'</table>'
            f'</body></html>'
        )
        if EmailService._is_dev():
            logger.info('[DEV-OTP] tipo=%s destinatario=%s codigo=%s', tipo, destinatario, codigo)
            return {'success': True, 'dev_otp': codigo, 'transport': 'dev-log'}
        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[destinatario],
                fail_silently=False,
                html_message=html_body,
            )
            logger.info('Email OTP enviado a %s (tipo=%s, sent=%s)', destinatario, tipo, sent)
            return {'success': sent >= 1, 'dev_otp': None, 'transport': 'real'}
        except Exception as exc:  # noqa: BLE001
            logger.exception('Fallo envio de email a %s: %s', destinatario, exc)
            return {'success': False, 'dev_otp': None, 'transport': 'error', 'error': str(exc)}

    @staticmethod
    def enviar_notificacion(destinatario, asunto, cuerpo, html=None):
        from_email = EmailService._from_email()
        if EmailService._is_dev():
            logger.info('[DEV-EMAIL] to=%s subject=%s', destinatario, asunto)
            return True
        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=from_email,
                recipient_list=[destinatario],
                fail_silently=True,
                html_message=html,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.exception('Fallo email transaccional a %s: %s', destinatario, exc)
            return False

    @staticmethod
    def enviar_bienvenida(destinatario, nombre=''):
        subject = 'Tu cuenta ha sido aprobada - Comunidad Zapotal'
        body = (
            f'Hola {nombre},\n\n'
            'Tu cuenta en la Comunidad Campesina Niño Dios de Zapotal ha sido aprobada por un administrador.\n\n'
            'Ya puedes iniciar sesion en la plataforma institucional:\n'
            'https://comunidadzapotal.com/login\n\n'
            'Tus credenciales de acceso son:\n'
            f'  - Correo electronico: {destinatario}\n'
            '  - Contrasena: la que utilizaste al momento de registrarte\n\n'
            'Si no realizaste este registro o tienes dudas, contactanos.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        html = (
            f'<div style="font-family:Inter,Arial,sans-serif;max-width:520px;margin:auto;padding:24px;'
            f'background:#fafafa;border-radius:12px;border:1px solid #eee">'
            f'<h2 style="color:#1a3a52">¡Bienvenido a Zapotal!</h2>'
            f'<p>Hola <strong>{nombre}</strong>,</p>'
            f'<p>Tu cuenta ha sido aprobada por un administrador.</p>'
            f'<p>Ya puedes iniciar sesion:</p>'
            f'<p style="text-align:center;margin:24px 0">'
            f'<a href="https://comunidadzapotal.com/login" '
            f'style="background:#1a3a52;color:#fff;padding:12px 24px;border-radius:8px;'
            f'text-decoration:none;font-weight:700">Iniciar sesion</a></p>'
            f'<p style="color:#555">Credenciales:</p>'
            f'<ul>'
            f'<li><strong>Correo:</strong> {destinatario}</li>'
            f'<li><strong>Contrasena:</strong> la que registraste (no podemos enviartela por seguridad)</li>'
            f'</ul>'
            f'<p style="color:#999;font-size:12px;margin-top:24px">Comunidad Campesina Niño Dios de Zapotal</p>'
            f'</div>'
        )
        return EmailService.enviar_notificacion(destinatario, subject, body, html=html)

    @staticmethod
    def enviar_rechazo(destinatario, motivo=''):
        subject = 'Tu solicitud de registro no fue aprobada - Comunidad Zapotal'
        body = (
            'Tu solicitud de registro no fue aprobada por el administrador.\n\n'
            f'Motivo: {motivo or "No especificado"}\n\n'
            'Si consideras que se trata de un error, contactanos.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        return EmailService.enviar_notificacion(destinatario, subject, body)

    @staticmethod
    def enviar_solicitud_baja(usuario):
        subject = 'Solicitud de baja recibida - Comunidad Zapotal'
        body = (
            f'Hola {usuario.nombre_completo},\n\n'
            'Hemos recibido tu solicitud de baja de la plataforma.\n'
            'Un administrador revisara tu solicitud y te notificaremos '
            'cuando sea procesada.\n\n'
            'Si no realizaste esta solicitud, contactanos de inmediato.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        html = _html_wrapper(
            header='Solicitud de baja recibida',
            paragraphs=[
                f'Hola <strong>{usuario.nombre_completo}</strong>,',
                'Hemos recibido tu solicitud de baja de la plataforma. '
                'Un administrador revisara tu solicitud y te notificaremos '
                'cuando sea procesada.',
            ],
            warning='Si no realizaste esta solicitud, contactanos de inmediato.',
        )
        return EmailService.enviar_notificacion(usuario.email, subject, body, html=html)

    @staticmethod
    def enviar_baja_aprobada(usuario, motivo=''):
        subject = 'Cuenta dada de baja - Comunidad Zapotal'
        body = (
            f'Hola {usuario.nombre_completo},\n\n'
            'Tu cuenta en la Comunidad Campesina Niño Dios de Zapotal '
            'ha sido dada de baja.\n'
            f'{"Motivo: " + motivo if motivo else ""}\n\n'
            'Si consideras que se trata de un error, contactanos.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        motivo_html = f'<p style="color:#555;margin:0 0 16px;font-size:15px"><strong>Motivo:</strong> {motivo}</p>' if motivo else ''
        html = _html_wrapper(
            header='Cuenta dada de baja',
            paragraphs=[
                f'Hola <strong>{usuario.nombre_completo}</strong>,',
                'Tu cuenta en la Comunidad Campesina Niño Dios de Zapotal '
                'ha sido dada de baja.',
            ],
            extra_html=motivo_html,
            warning='Si consideras que se trata de un error, contactanos.',
        )
        return EmailService.enviar_notificacion(usuario.email, subject, body, html=html)

    @staticmethod
    def enviar_cambio_password(usuario):
        subject = 'Contrasena actualizada - Comunidad Zapotal'
        body = (
            f'Hola {usuario.nombre_completo},\n\n'
            'Tu contrasena de acceso a la plataforma ha sido actualizada '
            'exitosamente.\n\n'
            'Si no realizaste este cambio, contactanos de inmediato.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        html = _html_wrapper(
            header='Contrasena actualizada',
            paragraphs=[
                f'Hola <strong>{usuario.nombre_completo}</strong>,',
                'Tu contrasena de acceso a la plataforma ha sido actualizada '
                'exitosamente.',
            ],
            warning='Si no realizaste este cambio, contactanos de inmediato.',
        )
        return EmailService.enviar_notificacion(usuario.email, subject, body, html=html)

    @staticmethod
    def enviar_2fa_activado(usuario):
        subject = 'Autenticacion en dos pasos activada - Comunidad Zapotal'
        body = (
            f'Hola {usuario.nombre_completo},\n\n'
            'La autenticacion en dos pasos (2FA) ha sido activada en tu cuenta.\n'
            'A partir de ahora, cada vez que inicies sesion se te pedira '
            'un codigo adicional de tu aplicación authenticator.\n\n'
            'Guarda tus codigos de respaldo en un lugar seguro.\n'
            'Si no activaste 2FA, contactanos de inmediato.\n\n'
            'Comunidad Campesina Niño Dios de Zapotal'
        )
        html = _html_wrapper(
            header='2FA activado',
            paragraphs=[
                f'Hola <strong>{usuario.nombre_completo}</strong>,',
                'La autenticacion en dos pasos (2FA) ha sido activada en tu cuenta.',
                'A partir de ahora, cada vez que inicies sesion se te pedira '
                'un codigo adicional de tu aplicacion authenticator.',
                'Guarda tus codigos de respaldo en un lugar seguro.',
            ],
            warning='Si no activaste 2FA, contactanos de inmediato.',
        )
        return EmailService.enviar_notificacion(usuario.email, subject, body, html=html)


# =====================================================================
# OTP SERVICE (solo email; SMS eliminado)
# =====================================================================

class OTPService:
    LONGITUD_CODIGO = 6
    VALIDEZ_MINUTOS = 5
    MAX_INTENTOS = 5
    COOLDOWN_REENVIO_SEGUNDOS = 60

    @classmethod
    def _generar_codigo(cls):
        return ''.join(str(secrets.randbelow(10)) for _ in range(cls.LONGITUD_CODIGO))

    @classmethod
    @transaction.atomic
    def generar_y_enviar(cls, usuario, tipo, destinatario=None, ip=None):
        if not destinatario:
            destinatario = usuario.email

        otp_prev = (
            OTPVerification.objects
            .filter(usuario=usuario, tipo=tipo, usado=False)
            .order_by('-creado_en')
            .first()
        )
        if otp_prev and (timezone.now() - otp_prev.creado_en).total_seconds() < cls.COOLDOWN_REENVIO_SEGUNDOS:
            restantes = cls.COOLDOWN_REENVIO_SEGUNDOS - int((timezone.now() - otp_prev.creado_en).total_seconds())
            raise ValidationError(
                f'Debes esperar {restantes} segundos antes de solicitar un nuevo codigo.'
            )

        # Invalidar OTPs anteriores del mismo tipo SOLO si NO fueron usados
        # (si el usuario ya ingreso el codigo anterior, se mantiene usado=True por el verificar())
        # Esto evita race condition cuando el email es lento: si el usuario tiene un codigo
        # valido sin usar y hace clic de nuevo, NO lo invalidamos (solo el nuevo cuenta).
        # El cooldown de 60s ya evita spam.
        # (comentario previo: update usado=True invalidaba todos, lo que hacia que
        #  emails lentos quedaran huerfanos con codigos que el backend rechazaba como "incorrecto")

        codigo = cls._generar_codigo()
        codigo_hash = hashlib.sha256(codigo.encode()).hexdigest()
        expira_en = timezone.now() + timedelta(minutes=cls.VALIDEZ_MINUTOS)

        otp = OTPVerification.objects.create(
            usuario=usuario,
            tipo=tipo,
            canal=OTPVerification.Canal.EMAIL,
            codigo_hash=codigo_hash,
            destinatario=destinatario,
            expira_en=expira_en,
            ip_solicitud=ip,
        )

        envio_result = EmailService.enviar_otp(destinatario, codigo, tipo)

        try:
            from apps.core.utils import log_audit_event
            log_audit_event(
                usuario=usuario,
                accion='OTP_SENT',
                descripcion=f'OTP enviado a {destinatario}',
                ip_address=ip,
                metadata={'tipo': tipo, 'canal': 'EMAIL'},
            )
        except Exception:  # noqa: BLE001
            pass

        return {'otp': otp, 'codigo': codigo, 'envio_result': envio_result}

    @classmethod
    def verificar(cls, usuario, tipo, codigo_ingresado, ip=None):
        """Verifica el codigo contra TODOS los OTPs activos del usuario.
        Si el codigo coincide con cualquiera de los OTPs no usados y no expirados,
        lo marca como usado y retorna True. Esto evita la race condition con
        emails lentos donde el usuario tiene multiples codigos en su inbox."""
        ahora = timezone.now()
        otps = list(
            OTPVerification.objects
            .filter(usuario=usuario, tipo=tipo, usado=False, expira_en__gt=ahora)
            .order_by('-creado_en')
        )
        if not otps:
            raise ValidationError('No hay codigo pendiente o ya expiro. Solicita uno nuevo.')

        # Buscar match contra cualquiera de los OTPs activos (no solo el ultimo)
        # Esto permite que el usuario use el codigo de cualquier email que recibio
        for otp in otps:
            if otp.verificar_codigo(codigo_ingresado):
                # Marcar TODOS los OTPs del mismo tipo como usados para evitar reuso
                OTPVerification.objects.filter(
                    usuario=usuario, tipo=tipo, usado=False
                ).update(usado=True)
                return True

        # Ningun OTP coincidio: incrementar intentos en el mas reciente y avisar
        otp = otps[0]
        otp.intentos += 1
        otp.save(update_fields=['intentos'])
        restantes = cls.MAX_INTENTOS - otp.intentos
        if restantes <= 0:
            otp.usado = True
            otp.save(update_fields=['usado'])
            raise ValidationError('Demasiados intentos. Solicita un nuevo codigo.')
        raise ValidationError(
            f'Codigo incorrecto. Intentos restantes: {restantes}'
        )


# =====================================================================
# TURNSTILE SERVICE
# =====================================================================

class TurnstileService:
    VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    @staticmethod
    def verify(token, ip=None):
        secret = getattr(settings, 'TURNSTILE_SECRET_KEY', '')
        site_key = getattr(settings, 'TURNSTILE_SITE_KEY', '')
        if not token:
            return False
        if not secret or secret.startswith('dev-') or secret == 'placeholder':
            logger.info('Turnstile dev: token aceptado sin validacion')
            return True
        if not site_key:
            return True
        if token == 'turnstile-fallback':
            logger.warning('Turnstile fallback: widget fallo (dominio no configurado?)')
            return True
        try:
            import requests
            resp = requests.post(
                TurnstileService.VERIFY_URL,
                data={'secret': secret, 'response': token, 'remoteip': ip or ''},
                timeout=10,
            )
            data = resp.json()
            return bool(data.get('success'))
        except Exception as exc:  # noqa: BLE001
            logger.exception('Turnstile fallo: %s', exc)
            return False


# =====================================================================
# 2FA SERVICE (TOTP real con pyotp)
# =====================================================================

class TwoFAService:
    ISSUER = 'Comunidad Zapotal'
    BACKUP_CODES_COUNT = 10

    @staticmethod
    def _import_pyotp():
        try:
            import pyotp
            return pyotp
        except ImportError:
            logger.error('pyotp no instalado. pip install pyotp qrcode')
            return None

    @classmethod
    def generar_secreto(cls):
        pyotp = cls._import_pyotp()
        if not pyotp:
            return None
        return pyotp.random_base32(length=32)

    @classmethod
    def otpauth_url(cls, usuario, secreto):
        pyotp = cls._import_pyotp()
        if not pyotp:
            return None
        return pyotp.TOTP(secreto).provisioning_uri(
            name=usuario.email,
            issuer_name=cls.ISSUER,
        )

    @classmethod
    def qr_code_base64(cls, otpauth_url):
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(otpauth_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode('ascii')
            return f'data:image/png;base64,{b64}'
        except ImportError:
            logger.error('qrcode no instalado. pip install qrcode')
            return None

    @classmethod
    def verificar_codigo(cls, secreto, codigo, ventana=1):
        pyotp = cls._import_pyotp()
        if not pyotp:
            return False
        try:
            return pyotp.TOTP(secreto).verify(str(codigo), valid_window=ventana)
        except Exception:  # noqa: BLE001
            return False

    @classmethod
    def backup_codes_plain(cls):
        return [secrets.token_hex(4).upper() for _ in range(cls.BACKUP_CODES_COUNT)]

    @classmethod
    def backup_codes_hashed(cls, plain_codes):
        return [hashlib.sha256(c.encode()).hexdigest() for c in plain_codes]

    @classmethod
    def iniciar_setup(cls, usuario):
        """Prepara 2FA: genera secreto, QR, backup codes. NO activa todavia."""
        secreto = cls.generar_secreto()
        if not secreto:
            return None
        otpauth = cls.otpauth_url(usuario, secreto)
        qr_b64 = cls.qr_code_base64(otpauth) if otpauth else None
        backup = cls.backup_codes_plain()
        return {
            'secret': secreto,
            'otpauth_url': otpauth,
            'qr_code_base64': qr_b64,
            'backup_codes': backup,
        }

    @classmethod
    def confirmar_setup(cls, usuario, secreto, codigo, ip=None):
        """Confirma 2FA: el usuario ingresa un codigo del authenticator. Si OK, activa."""
        if not cls.verificar_codigo(secreto, codigo):
            raise ValidationError('Codigo incorrecto. Verifica que escaneaste el QR correcto y que la hora del dispositivo sea correcta.')
        backup = cls.backup_codes_plain()
        backup_hash = cls.backup_codes_hashed(backup)
        usuario.two_factor_secret = secreto
        usuario.two_factor_backup_codes = backup_hash
        usuario.two_factor_enabled = True
        usuario.two_factor_confirmed_at = timezone.now()
        usuario.save(update_fields=[
            'two_factor_secret', 'two_factor_backup_codes',
            'two_factor_enabled', 'two_factor_confirmed_at',
        ])
        try:
            from apps.core.utils import log_audit_event
            log_audit_event(
                usuario=usuario, accion='TWO_FA_ENABLE', ip_address=ip,
                metadata={'backup_codes_count': len(backup)},
            )
        except Exception:  # noqa: BLE001
            pass
        return {'backup_codes': backup}

    @classmethod
    def validar(cls, usuario, codigo, ip=None):
        if not usuario.two_factor_enabled or not usuario.two_factor_secret:
            return False
        if cls.verificar_codigo(usuario.two_factor_secret, codigo):
            try:
                from apps.core.utils import log_audit_event
                log_audit_event(
                    usuario=usuario, accion='TWO_FA_VERIFY', ip_address=ip,
                    metadata={'metodo': 'totp'},
                )
            except Exception:  # noqa: BLE001
                pass
            return True
        codigo_hash = hashlib.sha256(str(codigo).encode()).hexdigest()
        codes = list(usuario.two_factor_backup_codes or [])
        for idx, h in enumerate(codes):
            if h == codigo_hash:
                codes.pop(idx)
                usuario.two_factor_backup_codes = codes
                usuario.save(update_fields=['two_factor_backup_codes'])
                try:
                    from apps.core.utils import log_audit_event
                    log_audit_event(
                        usuario=usuario, accion='TWO_FA_VERIFY', ip_address=ip,
                        metadata={'metodo': 'backup_code'},
                    )
                except Exception:  # noqa: BLE001
                    pass
                return True
        return False

    @classmethod
    def desactivar(cls, usuario, password_actual, ip=None):
        if not usuario.check_password(password_actual):
            raise ValidationError('Contrasena incorrecta.')
        usuario.two_factor_enabled = False
        usuario.two_factor_secret = ''
        usuario.two_factor_backup_codes = []
        usuario.two_factor_confirmed_at = None
        usuario.save(update_fields=[
            'two_factor_enabled', 'two_factor_secret',
            'two_factor_backup_codes', 'two_factor_confirmed_at',
        ])
        try:
            from apps.core.utils import log_audit_event
            log_audit_event(usuario=usuario, accion='TWO_FA_DISABLE', ip_address=ip)
        except Exception:  # noqa: BLE001
            pass
