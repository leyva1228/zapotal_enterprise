"""Helpers de envio de correo electronico via Resend (django-anymail).

Los views institucionales importan :func:`notificar_admin_mensaje_contacto`
y :func:`notificar_admin_reclamo` para enviar una notificacion cada vez
que llega un nuevo mensaje a traves de los formularios publicos.

Si la API de Resend falla, el error se registra en ``logging`` pero la
creacion del registro en la DB se mantiene exitosa: el usuario no
debe perder su mensaje por una caida del SMTP.

Destino de los correos (orden de precedencia):
    1. ``settings.EMAIL_DESTINO_TEMPORAL``  (override explicito)
    2. ``ConfiguracionComunidad.email_contacto``  (buzon institucional)
    3. ``settings.ADMIN_EMAILS[0]``  (fallback administrativo)
"""
from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# ----- V2.2: sanitizacion de asuntos para evitar CRLF injection -----

def _sanitize_subject(texto: str, max_len: int = 200) -> str:
    """Limpia un asunto de email para evitar inyeccion de headers SMTP
    (CR/LF permitirian inyectar Bcc:, Cc:, etc).

    - Remueve CR/LF.
    - Colapsa espacios.
    - Trunca a ``max_len`` caracteres.
    - Si queda vacio, retorna el fallback.
    """
    fallback = 'Notificacion Comunidad Zapotal'
    if not texto:
        return fallback
    limpio = texto.replace('\r', ' ').replace('\n', ' ').strip()
    limpio = ' '.join(limpio.split())
    if not limpio:
        return fallback
    return limpio[:max_len] if len(limpio) > max_len else limpio

from apps.reports.models import LibroReclamacion

from .models_institucionales import ConfiguracionComunidad, MensajeContacto

logger = logging.getLogger(__name__)


def _from_email() -> str:
    """Remitente con formato amigable. Resend exige que el dominio este
    verificado en el panel de Resend, pero el nombre entre comillas no
    rompe el formato RFC 5322."""
    nombre = getattr(settings, 'RESEND_FROM_NAME', 'Comunidad Zapotal')
    correo = getattr(settings, 'RESEND_FROM_EMAIL', 'noreply@comunidadzapotal.com')
    if not correo:
        return 'noreply@comunidadzapotal.com'
    if '<' in correo:
        return correo
    return f'"{nombre}" <{correo}>'


def _resolver_destinatario(
    cfg: Optional[ConfiguracionComunidad] = None,
    tipo: str = 'contacto',
) -> str:
    """Devuelve el buzon destino respetando el orden de precedencia.

    :param cfg: instancia de :class:`ConfiguracionComunidad` (o ``None``).
    :param tipo: 'contacto' | 'reclamo' | 'denuncia' (para logs).
    :returns: direccion de email, o ``''`` si no hay destinatario.
    """
    # 1. Override explicito (util cuando el dominio institucional
    #    aun no esta operativo).
    override = (getattr(settings, 'EMAIL_DESTINO_TEMPORAL', '') or '').strip()
    if override:
        return override

    # 2. ConfiguracionComunidad (campo email_contacto).
    if cfg is None:
        try:
            cfg = ConfiguracionComunidad.get_solo()
        except Exception:  # pragma: no cover
            cfg = None
    if cfg and cfg.email_contacto:
        return cfg.email_contacto

    # 3. Fallback administrativo (settings.ADMIN_EMAILS).
    admins = getattr(settings, 'ADMIN_EMAILS', None)
    if isinstance(admins, (list, tuple)) and admins:
        return admins[0]
    if isinstance(admins, str) and admins:
        return admins.split(',')[0].strip()
    return ''


def notificar_admin_mensaje_contacto(msg: MensajeContacto) -> bool:
    """Envia una notificacion al buzon configurado.

    Retorna ``True`` si el correo se entrego al backend (no garantiza
    entrega final, eso depende de Resend). Retorna ``False`` si falla
    o si no hay destinatario configurado.
    """
    try:
        cfg = ConfiguracionComunidad.get_solo()
    except Exception:  # pragma: no cover
        cfg = None

    destinatario = _resolver_destinatario(cfg, tipo='contacto')
    if not destinatario:
        logger.warning(
            'No hay destinatario configurado; no se envia notificacion '
            'para el mensaje de contacto id=%s.',
            msg.id,
        )
        return False

    ctx = {
        'mensaje': msg,
        'comunidad_nombre': cfg.nombre_oficial if cfg else 'Comunidad Zapotal',
        'admin_url': getattr(settings, 'FRONTEND_ADMIN_URL', '/admin/'),
        'destinatario': destinatario,
    }
    html_body = render_to_string(
        'comunidad/email/mensaje_contacto_notificacion.html',
        ctx,
    )
    plain_body = strip_tags(html_body) or (
        f'Nuevo mensaje de contacto\n\n'
        f'Nombre: {msg.nombre}\n'
        f'Email: {msg.email}\n'
        f'Telefono: {msg.telefono or "-"}\n'
        f'Asunto: {msg.asunto}\n\n'
        f'Mensaje:\n{msg.mensaje}\n'
    )
    asunto = _sanitize_subject(f'[Contacto Web] {msg.asunto} - de {msg.nombre}')

    try:
        email = EmailMessage(
            subject=asunto,
            body=plain_body,
            from_email=_from_email(),
            to=[destinatario],
            reply_to=[msg.email] if msg.email else None,
        )
        email.content_subtype = 'html'
        email.body = html_body
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception(
            'Fallo el envio de notificacion de contacto (id=%s): %s',
            msg.id,
            exc,
        )
        return False


def notificar_admin_reclamo(rec: LibroReclamacion) -> bool:
    """Envia una notificacion al admin por un nuevo Libro de Reclamaciones.

    Misma politica de destinos y de resiliencia que
    :func:`notificar_admin_mensaje_contacto`.
    """
    try:
        cfg = ConfiguracionComunidad.get_solo()
    except Exception:  # pragma: no cover
        cfg = None

    destinatario = _resolver_destinatario(cfg, tipo='reclamo')
    if not destinatario:
        logger.warning(
            'No hay destinatario configurado; no se envia notificacion '
            'para el reclamo id=%s.',
            rec.id,
        )
        return False

    ctx = {
        'reclamo': rec,
        'comunidad_nombre': cfg.nombre_oficial if cfg else 'Comunidad Zapotal',
        'admin_url': getattr(settings, 'FRONTEND_ADMIN_URL', '/admin/'),
        'destinatario': destinatario,
    }
    # Plantilla opcional; si no existe, fallback al cuerpo plano.
    try:
        html_body = render_to_string(
            'comunidad/email/libro_reclamacion_notificacion.html',
            ctx,
        )
    except Exception:
        html_body = ''
    plain_body = strip_tags(html_body) if html_body else (
        f'Nueva reclamacion en el Libro de Reclamaciones\n\n'
        f'Consumidor: {rec.nombre}\n'
        f'Email: {rec.email}\n'
        f'Telefono: {rec.telefono or "-"}\n'
        f'Direccion: {rec.direccion or "-"}\n'
        f'Tipo: {rec.tipo}\n'
        f'Descripcion:\n{rec.descripcion}\n'
    )
    asunto = _sanitize_subject(f'[Libro de Reclamaciones] {rec.tipo} - de {rec.nombre}')

    try:
        email = EmailMessage(
            subject=asunto,
            body=plain_body,
            from_email=_from_email(),
            to=[destinatario],
            reply_to=[rec.email] if rec.email else None,
        )
        email.content_subtype = 'html'
        email.body = html_body or plain_body
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception(
            'Fallo el envio de notificacion de reclamo (id=%s): %s',
            rec.id,
            exc,
        )
        return False


def enviar_respuesta_reclamo(rec, respuesta, admin_user) -> dict:
    """Envia la respuesta del admin al email del consumidor via Resend.

    V2.2: retorna ``dict(enviado, asunto, cuerpo_html, cuerpo_texto)``
    para que el admin pueda ver el preview del email enviado.

    El email sale con ``reply_to=[admin_user.email]`` para que cuando el
    consumidor responda, llegue al buzon del admin.
    """
    try:
        cfg = ConfiguracionComunidad.get_solo()
    except Exception:
        cfg = None

    ctx = {
        'reclamo': rec,
        'respuesta': respuesta,
        'admin_nombre': (
            admin_user.get_full_name() if hasattr(admin_user, 'get_full_name') and admin_user.get_full_name()
            else admin_user.email
        ),
        'comunidad_nombre': cfg.nombre_oficial if cfg else 'Comunidad Zapotal',
    }
    try:
        html_body = render_to_string(
            'comunidad/email/libro_reclamacion_respuesta.html',
            ctx,
        )
    except Exception:
        html_body = ''
    plain_body = strip_tags(html_body) if html_body else (
        f'Estimado/a {rec.nombre},\n\n'
        f'Respuesta a su reclamo {rec.numero_reclamo}:\n\n'
        f'{respuesta}\n\n'
        f'-- \nComunidad Campesina Zapotal'
    )
    asunto = f'Respuesta a su reclamo {rec.numero_reclamo} - Comunidad Zapotal'

    try:
        email = EmailMessage(
            subject=asunto,
            body=plain_body,
            from_email=_from_email(),
            to=[rec.email],
            reply_to=[admin_user.email] if admin_user.email else None,
        )
        email.content_subtype = 'html'
        email.body = html_body or plain_body
        email.send(fail_silently=False)
        return {
            'enviado': True,
            'asunto': asunto,
            'cuerpo_html': html_body or plain_body,
            'cuerpo_texto': plain_body,
        }
    except Exception as exc:
        logger.exception(
            'Fallo el envio de respuesta de reclamo %s: %s',
            rec.numero_reclamo, exc,
        )
        return {
            'enviado': False,
            'asunto': asunto,
            'cuerpo_html': html_body or plain_body,
            'cuerpo_texto': plain_body,
            'error': str(exc),
        }


def notificar_consumidor_cambio_estado_reclamo(rec, estado_anterior, estado_nuevo) -> bool:
    """Envia email al consumidor cuando cambia el estado de su reclamo.

    Cumplimiento Ley 29571 Art. 24: el consumidor debe ser notificado
    de cualquier cambio de estado.
    """
    try:
        cfg = ConfiguracionComunidad.get_solo()
    except Exception:
        cfg = None

    ctx = {
        'reclamo': rec,
        'estado_anterior': estado_anterior,
        'estado_nuevo': estado_nuevo,
        'comunidad_nombre': cfg.nombre_oficial if cfg else 'Comunidad Zapotal',
    }
    try:
        html_body = render_to_string(
            'comunidad/email/libro_reclamacion_cambio_estado.html',
            ctx,
        )
    except Exception:
        html_body = ''
    plain_body = strip_tags(html_body) if html_body else (
        f'Estimado/a {rec.nombre},\n\n'
        f'Su reclamo {rec.numero_reclamo} cambio de estado: '
        f'{estado_anterior} -> {estado_nuevo}.\n\n'
        f'-- \nComunidad Campesina Zapotal'
    )
    asunto = f'Actualizacion de su reclamo {rec.numero_reclamo} - {estado_nuevo}'

    try:
        email = EmailMessage(
            subject=asunto,
            body=plain_body,
            from_email=_from_email(),
            to=[rec.email],
        )
        email.content_subtype = 'html'
        email.body = html_body or plain_body
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception(
            'Fallo envio de cambio de estado reclamo %s: %s',
            rec.numero_reclamo, exc,
        )
        return False


def enviar_respuesta_contacto(msg: MensajeContacto, respuesta: str, admin_user) -> bool:
    """Envia la respuesta del admin al email del visitante via Resend.

    El email sale con ``reply_to=[admin_user.email]`` para que cuando el
    visitante responda, llegue al buzon del admin (no al noreply).

    Retorna ``True`` si el correo se entrego al backend, ``False`` si falla
    o si no hay destinatario.
    """
    try:
        cfg = ConfiguracionComunidad.get_solo()
    except Exception:
        cfg = None

    ctx = {
        'mensaje': msg,
        'respuesta': respuesta,
        'admin_nombre': (
            admin_user.get_full_name() if hasattr(admin_user, 'get_full_name') and admin_user.get_full_name()
            else admin_user.email
        ),
        'comunidad_nombre': cfg.nombre_oficial if cfg else 'Comunidad Zapotal',
    }
    try:
        html_body = render_to_string(
            'comunidad/email/mensaje_contacto_respuesta.html',
            ctx,
        )
    except Exception:
        html_body = ''
    plain_body = strip_tags(html_body) if html_body else (
        f'Estimado/a {msg.nombre},\n\n'
        f'Respuesta a su mensaje de contacto:\n\n'
        f'{respuesta}\n\n'
        f'-- \nComunidad Campesina Zapotal'
    )
    asunto = _sanitize_subject(f'Re: {msg.asunto} - Comunidad Zapotal')

    try:
        email = EmailMessage(
            subject=asunto,
            body=plain_body,
            from_email=_from_email(),
            to=[msg.email],
            reply_to=[admin_user.email] if admin_user.email else None,
        )
        email.content_subtype = 'html'
        email.body = html_body or plain_body
        email.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception(
            'Fallo el envio de respuesta de contacto (id=%s): %s',
            msg.id,
            exc,
        )
        return False
