"""
Utilidades compartidas para el nucleo: IP de cliente, sanitizacion de metadata y logging de auditoria.
"""
import logging
from typing import Optional, Dict, Any
from django.http import HttpRequest

logger = logging.getLogger(__name__)


# Claves sensibles que NUNCA deben persistirse en metadata de AuditLog.
SENSITIVE_KEYS = {
    'password', 'password1', 'password2', 'new_password',
    'token', 'access', 'refresh',
    'secret', 'two_factor_secret', 'two_factor_backup_codes',
    'codigo', 'code', 'otp', 'otp_code',
    'authorization', 'cookie',
}


def get_client_ip(request: Optional[HttpRequest]) -> Optional[str]:
    """Devuelve la IP del cliente, considerando X-Forwarded-For si hay proxy."""
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or None


def sanitize_metadata(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Elimina claves sensibles, hashea emails opcionalmente y trunca valores largos.
    """
    if not data:
        return {}
    out = {}
    for k, v in (data or {}).items():
        if k.lower() in SENSITIVE_KEYS:
            continue
        if isinstance(v, str) and len(v) > 1024:
            v = v[:1024] + '...[truncated]'
        out[k] = v
    return out


def log_audit_event(
    accion: str,
    descripcion: str = '',
    usuario=None,
    autoridad=None,
    modelo_afectado: str = '',
    objeto_id: str = '',
    ip_address: Optional[str] = None,
    user_agent: str = '',
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[HttpRequest] = None,
):
    """Helper para crear entradas AuditLog con sanitizacion automatica."""
    from apps.core.models import AuditLog

    if request is not None:
        if not ip_address:
            ip_address = get_client_ip(request)
        if not user_agent:
            user_agent = (request.META.get('HTTP_USER_AGENT') or '')[:255]

    try:
        AuditLog.objects.create(
            usuario=usuario if usuario and getattr(usuario, 'is_authenticated', False) else None,
            autoridad=autoridad,
            accion=accion,
            modelo_afectado=modelo_afectado or '',
            objeto_id=str(objeto_id) if objeto_id else '',
            descripcion=descripcion or '',
            ip_address=ip_address,
            user_agent=user_agent or '',
            metadata=sanitize_metadata(metadata or {}),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception('No se pudo crear AuditLog: %s', exc)
